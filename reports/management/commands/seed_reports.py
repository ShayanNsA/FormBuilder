from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from user.models import User
from form.models import Form, Category, Question
from process.models import Process, ProcessStep
from submission.models import (
    FormSubmission,
    Answer,
    ProcessExecution,
    ExecutionStatus,
)
from submission.constants import QuestionType, ProcessType

from reports.models import ScheduledReport, VisitLogs


class Command(BaseCommand):

    def handle(self, *args, **options):

        # ---------------------------------
        # User
        # ---------------------------------

        user, _ = User.objects.get_or_create(
            username='reports_test_user',
            defaults={
                'email': 'reports@test.com',
            }
        )

        if not user.has_usable_password():
            user.set_password('Test12345')
            user.save()

        # ---------------------------------
        # Category
        # ---------------------------------

        category, _ = Category.objects.get_or_create(
            user=user,
            title='Reports Test Category',
            defaults={
                'description': 'Category for Reports testing',
            }
        )

        # ---------------------------------
        # Form
        # ---------------------------------

        form, _ = Form.objects.get_or_create(
            user=user,
            title='Reports Test Form',
            defaults={
                'description': 'Form created for Reports testing',
                'is_public': True,
                'is_deleted': False,
            }
        )

        form.categories.add(category)

        # ---------------------------------
        # Questions
        # ---------------------------------

        questions = [
            {
                'title': 'What is your name?',
                'question_type': QuestionType.TEXT,
                'question_options': [],
            },
            {
                'title': 'What is your age?',
                'question_type': QuestionType.NUMBER,
                'question_options': [],
            },
            {
                'title': 'What is your favorite color?',
                'question_type': QuestionType.SELECT,
                'question_options': [
                    'Red',
                    'Blue',
                    'Green',
                ],
            },
            {
                'title': 'Which sports do you like?',
                'question_type': QuestionType.CHECKBOX,
                'question_options': [
                    'Football',
                    'Table Tennis',
                    'Swimming',
                ],
            },
        ]

        for question_data in questions:

            Question.objects.get_or_create(
                form=form,
                title=question_data['title'],
                defaults={
                    'question_type': question_data['question_type'],
                    'question_options': question_data['question_options'],
                    'is_required': True,
                }
            )

        # ---------------------------------
        # Process
        # ---------------------------------

        process, _ = Process.objects.get_or_create(
            user=user,
            title='Reports Test Process',
            defaults={
                'description': 'Process created for Reports testing',
                'process_type': ProcessType.LINEAR,
                'is_public': True,
                'is_deleted': False,
            }
        )

        process.categories.add(category)

        ProcessStep.objects.get_or_create(
            process=process,
            form=form,
            defaults={
                'step_order': 1,
            }
        )

        # ---------------------------------
        # Scheduled Reports
        # ---------------------------------

        scheduled_reports = [
            ('form', 'daily'),
            ('form', 'weekly'),
            ('process', 'monthly'),
        ]

        for report_type, frequency in scheduled_reports:

            ScheduledReport.objects.get_or_create(
                user=user,
                report_type=report_type,
                frequency=frequency,
            )

        # ---------------------------------
        # Visit Logs
        # ---------------------------------

        form_content_type = ContentType.objects.get_for_model(Form)
        process_content_type = ContentType.objects.get_for_model(Process)

        for _ in range(3):

            VisitLogs.objects.create(
                content_type=form_content_type,
                object_id=form.id,
                user=user,
                visitor_ip='127.0.0.1',
            )

        for _ in range(2):

            VisitLogs.objects.create(
                content_type=process_content_type,
                object_id=process.id,
                user=user,
                visitor_ip='127.0.0.1',
            )

        # ---------------------------------
        # Form Submission
        # ---------------------------------

        form_submission = FormSubmission.objects.create(
            form=form,
            user=user,
            submitter_ip='127.0.0.1',
        )

        for question in form.questions.all():

            value_text = None
            value_number = None
            value_json = None

            if question.question_type == QuestionType.TEXT:

                value_text = 'Farshid'

            elif question.question_type == QuestionType.TEXTAREA:

                value_text = 'This is a sample paragraph.'

            elif question.question_type == QuestionType.NUMBER:

                value_number = 25

            elif question.question_type in (
                QuestionType.SELECT,
                QuestionType.RADIO,
            ):

                value_json = question.question_options[0]

            elif question.question_type == QuestionType.CHECKBOX:

                value_json = question.question_options[:2]

            Answer.objects.create(
                form_submission=form_submission,
                question=question,
                value_text=value_text,
                value_number=value_number,
                value_json=value_json,
            )

        # ---------------------------------
        # Process Execution
        # ---------------------------------

        execution = ProcessExecution.objects.create(
            process=process,
            user=user,
            status=ExecutionStatus.COMPLETED,
            current_step_order=1,
            completed_at=timezone.now(),
        )

        # ---------------------------------
        # Process Form Submission
        # ---------------------------------

        process_submission = FormSubmission.objects.create(
            form=form,
            process_execution=execution,
            user=user,
            submitter_ip='127.0.0.1',
        )

        for question in form.questions.all():

            value_text = None
            value_number = None
            value_json = None

            if question.question_type == QuestionType.TEXT:

                value_text = 'Process Test User'

            elif question.question_type == QuestionType.TEXTAREA:

                value_text = 'Process sample paragraph.'

            elif question.question_type == QuestionType.NUMBER:

                value_number = 50

            elif question.question_type in (
                QuestionType.SELECT,
                QuestionType.RADIO,
            ):

                value_json = question.question_options[1]

            elif question.question_type == QuestionType.CHECKBOX:

                value_json = question.question_options[:2]

            Answer.objects.create(
                form_submission=process_submission,
                question=question,
                value_text=value_text,
                value_number=value_number,
                value_json=value_json,
            )

        # ---------------------------------
        # Finish
        # ---------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                'Reports seed data created successfully.'
            )
        )

        self.stdout.write(
            f'User: {user.username}'
        )

        self.stdout.write(
            f'Form ID: {form.id}'
        )

        self.stdout.write(
            f'Process ID: {process.id}'
        )