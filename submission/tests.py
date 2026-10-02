from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from form.models import Form, Question
from process.models import Process, ProcessStep
from .constants import ProcessType, QuestionType
from .models import Answer, ExecutionStatus, FormSubmission, ProcessExecution


User = get_user_model()


# create a test user
def make_user(username):
    return User.objects.create_user(username=username, password="pass12345")


# create a public test form
def make_form(creator, slug):
    return Form.objects.create(creator=creator, title=slug, slug=slug, is_public=True)


# create a question for a form
def make_question(form, text, qtype, order, required=True, options=None):
    return Question.objects.create(
        form=form,
        question_text=text,
        question_type=qtype,
        is_required=required,
        order=order,
        options=options or [],
    )


# extract items array from paginated or standard response data
def items(response):
    data = response.data
    return data["results"] if isinstance(data, dict) and "results" in data else data


# database constraints on answer model value fields
class AnswerConstraintTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        owner = make_user("owner")
        cls.form = make_form(owner, "constraint-form")
        cls.question = make_question(cls.form, "q", QuestionType.TEXT, 1)
        cls.submission = FormSubmission.objects.create(form=cls.form, user=owner)

    # ensure an answer with exactly one value field is successfully saved
    def test_single_value_is_allowed(self):
        Answer.objects.create(
            form_submission=self.submission, question=self.question, value_text="ok"
        )
        self.assertEqual(Answer.objects.count(), 1)

    # ensure filling multiple value fields raises an error
    def test_two_values_are_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Answer.objects.create(
                form_submission=self.submission,
                question=self.question,
                value_text="a",
                value_number=Decimal("1"),
            )

    # ensure creating an answer without any value field raises an error
    def test_no_value_is_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Answer.objects.create(
                form_submission=self.submission, question=self.question
            )


# API endpoints for form submissions, validation and permissions
class FormSubmissionApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = make_user("owner")
        cls.user = make_user("user")
        cls.other = make_user("other")
        cls.form = make_form(cls.owner, "survey")
        cls.name_q = make_question(cls.form, "name", QuestionType.TEXT, 1)
        cls.age_q = make_question(cls.form, "age", QuestionType.NUMBER, 2)
        cls.city_q = make_question(
            cls.form, "city", QuestionType.SELECT, 3, options=["tehran", "shiraz"]
        )
        cls.hobby_q = make_question(
            cls.form, "hobby", QuestionType.CHECKBOX, 4, required=False,
            options=["a", "b", "c"],
        )
        cls.url = reverse("submission:submission-list")

    # generate submission request payload with optional overrides
    def payload(self, **overrides):
        values = {
            self.name_q.id: "Ali",
            self.age_q.id: 30,
            self.city_q.id: "tehran",
            self.hobby_q.id: ["a", "c"],
        }
        values.update(overrides)
        return {
            "form": self.form.id,
            "answers": [{"question": qid, "value": v} for qid, v in values.items()],
        }

    # ensure unauthenticated users cannot submit a form
    def test_requires_authentication(self):
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    # verify successful submission and correct storage across all question types
    def test_submit_all_question_types(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, self.payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        submission = FormSubmission.objects.get(pk=response.data["id"])
        self.assertEqual(submission.user, self.user)
        answers = {a.question_id: a for a in submission.answers.all()}
        self.assertEqual(answers[self.name_q.id].value_text, "Ali")
        self.assertEqual(answers[self.age_q.id].value_number, Decimal("30"))
        self.assertEqual(answers[self.city_q.id].value_json, "tehran")
        self.assertEqual(answers[self.hobby_q.id].value_json, ["a", "c"])

    # ensure empty optional answers are safely skipped without creating records
    def test_optional_empty_answer_is_skipped(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url, self.payload(**{self.hobby_q.id: []}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 3)

    # ensure missing or empty required questions triggers a 400 error
    def test_required_question_missing(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url, self.payload(**{self.name_q.id: ""}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FormSubmission.objects.count(), 0)

    # ensure submitting an option not in select choices fails validation
    def test_invalid_select_option(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url, self.payload(**{self.city_q.id: "paris"}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ensure invalid choices in multi-select checkbox answers triggers a 400 error
    def test_invalid_checkbox_option(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url, self.payload(**{self.hobby_q.id: ["a", "zzz"]}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ensure non-numeric input for a number question triggers a 400 error
    def test_number_rejects_text(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url, self.payload(**{self.age_q.id: "abc"}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ensure submissions are only visible to the submitter and the form creator
    def test_visibility_of_submissions(self):
        self.client.force_authenticate(self.user)
        self.client.post(self.url, self.payload(), format="json")

        self.client.force_authenticate(self.other)
        self.assertEqual(len(items(self.client.get(self.url))), 0)

        self.client.force_authenticate(self.owner)
        self.assertEqual(len(items(self.client.get(self.url))), 1)

    # ensure only the form creator can review and mark submissions as reviewed
    def test_only_form_creator_can_review(self):
        self.client.force_authenticate(self.user)
        submission_id = self.client.post(self.url, self.payload(), format="json").data["id"]
        review_url = reverse("submission:submission-review", args=[submission_id])

        response = self.client.post(review_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.owner)
        response = self.client.post(review_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(FormSubmission.objects.get(pk=submission_id).is_reviewed)


# Test suite: Multi-step process executions, step ordering, and lifecycle
class ProcessExecutionApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = make_user("owner")
        cls.user = make_user("user")
        cls.other = make_user("other")
        cls.form1 = make_form(cls.owner, "step-1")
        cls.form2 = make_form(cls.owner, "step-2")
        cls.q1 = make_question(cls.form1, "q1", QuestionType.TEXT, 1)
        cls.q2 = make_question(cls.form2, "q2", QuestionType.TEXT, 1)
        cls.linear = cls.make_process("linear", ProcessType.LINEAR)
        cls.free = cls.make_process("free", ProcessType.FREE)
        cls.executions_url = reverse("submission:execution-list")
        cls.submissions_url = reverse("submission:submission-list")

    @classmethod
    def make_process(cls, title, process_type):
        process = Process.objects.create(
            creator=cls.owner, title=title, process_type=process_type, is_public=True
        )
        ProcessStep.objects.create(process=process, form=cls.form1, step_order=1)
        ProcessStep.objects.create(process=process, form=cls.form2, step_order=2)
        return process


    def start(self, process):
        return self.client.post(
            self.executions_url, {"process": process.id}, format="json"
        )

    def submit(self, form, question, execution_id):
        return self.client.post(
            self.submissions_url,
            {
                "form": form.id,
                "process_execution": execution_id,
                "answers": [{"question": question.id, "value": "x"}],
            },
            format="json",
        )

    # ensure linear processes enforce step order from start to completion
    def test_linear_process_enforces_order(self):
        self.client.force_authenticate(self.user)
        execution_id = self.start(self.linear).data["id"]

        response = self.submit(self.form2, self.q2, execution_id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.submit(self.form1, self.q1, execution_id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        execution = ProcessExecution.objects.get(pk=execution_id)
        self.assertEqual(execution.current_step_order, 2)
        self.assertEqual(execution.status, ExecutionStatus.IN_PROGRESS)

        response = self.submit(self.form2, self.q2, execution_id)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        execution.refresh_from_db()
        self.assertEqual(execution.status, ExecutionStatus.COMPLETED)
        self.assertIsNotNone(execution.completed_at)

    # ensure free processes allow steps to be submitted in any order
    def test_free_process_allows_any_order(self):
        self.client.force_authenticate(self.user)
        execution_id = self.start(self.free).data["id"]

        self.assertEqual(
            self.submit(self.form2, self.q2, execution_id).status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            self.submit(self.form1, self.q1, execution_id).status_code,
            status.HTTP_201_CREATED,
        )
        execution = ProcessExecution.objects.get(pk=execution_id)
        self.assertEqual(execution.status, ExecutionStatus.COMPLETED)

    # ensure a single process step cannot be submitted more than once
    def test_step_cannot_be_submitted_twice(self):
        self.client.force_authenticate(self.user)
        execution_id = self.start(self.free).data["id"]
        self.submit(self.form1, self.q1, execution_id)
        response = self.submit(self.form1, self.q1, execution_id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ensure users cannot have multiple active executions of the same process
    def test_cannot_start_two_active_executions(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.start(self.linear).status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.start(self.linear).status_code, status.HTTP_400_BAD_REQUEST)

    # Ensure users cannot submit form steps for another user's process execution
    def test_cannot_use_another_users_execution(self):
        self.client.force_authenticate(self.user)
        execution_id = self.start(self.linear).data["id"]

        self.client.force_authenticate(self.other)
        response = self.submit(self.form1, self.q1, execution_id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

