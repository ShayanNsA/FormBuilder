from datetime import timedelta
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from reports.models import VisitLogs, ScheduledReport
from user.models import User
from form.models import Form, Question
from process.models import Process, ProcessStep
from submission.models import (
    FormSubmission,
    Answer,
    ProcessExecution,
    ExecutionStatus,
)
from submission.constants import QuestionType, ProcessType


class ReportsTest(TestCase):

    def setUp(self):
        cache.clear()

        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='Test12345',
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='Test12345',
        )

        self.client.force_authenticate(user=self.user)

        self.form = Form.objects.create(
            user=self.user,
            title='Test Form',
            description='Test Form for reports',
            is_public=True,
            is_deleted=False,
        )

        self.text_question = Question.objects.create(
            form=self.form,
            title='Name',
            question_type=QuestionType.TEXT,
            is_required=True,
        )

        self.number_question = Question.objects.create(
            form=self.form,
            title='Age',
            question_type=QuestionType.NUMBER,
            is_required=True,
        )

        self.select_question = Question.objects.create(
            form=self.form,
            title='Color',
            question_type=QuestionType.SELECT,
            question_options=['Red', 'Blue'],
            is_required=True,
        )

        self.checkbox_question = Question.objects.create(
            form=self.form,
            title='Sport',
            question_type=QuestionType.CHECKBOX,
            question_options=['Football', 'Table Tennis'],
            is_required=False,
        )

        self.process = Process.objects.create(
            user=self.user,
            title='Test Process',
            description='Test Process for reports',
            process_type=ProcessType.LINEAR,
            is_public=True,
            is_deleted=False,
        )

        ProcessStep.objects.create(
            process=self.process,
            form=self.form,
            step_order=1,
        )

        self.form_submission = FormSubmission.objects.create(
            form=self.form,
            user=self.user,
        )

        Answer.objects.create(
            form_submission=self.form_submission,
            question=self.number_question,
            value_number=25,
        )

        Answer.objects.create(
            form_submission=self.form_submission,
            question=self.text_question,
            value_text='farshid',
        )

        Answer.objects.create(
            form_submission=self.form_submission,
            question=self.select_question,
            value_json='Red',
        )

        Answer.objects.create(
            form_submission=self.form_submission,
            question=self.checkbox_question,
            value_json=['Football', 'Table Tennis'],
        )

        self.execution = ProcessExecution.objects.create(
            process=self.process,
            user=self.user,
            status=ExecutionStatus.COMPLETED,
            current_step_order=1,
            completed_at=timezone.now(),
        )

        self.process_submission = FormSubmission.objects.create(
            form=self.form,
            process_execution=self.execution,
            user=self.user,
        )

        Answer.objects.create(
            form_submission=self.process_submission,
            question=self.text_question,
            value_text='Test',
        )

        Answer.objects.create(
            form_submission=self.process_submission,
            question=self.number_question,
            value_number=50,
        )

        Answer.objects.create(
            form_submission=self.process_submission,
            question=self.select_question,
            value_json='Blue',
        )

        Answer.objects.create(
            form_submission=self.process_submission,
            question=self.checkbox_question,
            value_json=['Football', 'Table Tennis'],
        )

        form_content_type = ContentType.objects.get_for_model(Form)
        process_content_type = ContentType.objects.get_for_model(Process)

        VisitLogs.objects.create(
            content_type=form_content_type,
            object_id=self.form.id,
            user=self.user,
            visitor_ip='127.0.0.1',
        )

        VisitLogs.objects.create(
            content_type=form_content_type,
            object_id=self.form.id,
            user=self.user,
            visitor_ip='127.0.0.1',
        )

        VisitLogs.objects.create(
            content_type=process_content_type,
            object_id=self.process.id,
            user=self.user,
            visitor_ip='127.0.0.1',
        )

        self.scheduled_report = ScheduledReport.objects.create(
            user=self.user,
            report_type='form',
            frequency='daily',
        )

    def test_scheduled_report(self):
        response = self.client.get(
            '/api/reports/scheduled-reports/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.post(
            '/api/reports/scheduled-reports/',
            {
                'report_type': 'process',
                'frequency': 'weekly',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['report_type'], 'process')
        self.assertEqual(response.data['frequency'], 'weekly')

    def test_visit_logs(self):
        response = self.client.get(
            '/api/reports/visit-logs/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_form_report(self):
        response = self.client.get(
            f'/api/reports/forms/{self.form.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['form_id'], self.form.id)
        self.assertEqual(response.data['title'], 'Test Form')
        self.assertEqual(response.data['submission_count'], 2)
        self.assertEqual(response.data['visit_count'], 2)

    def test_form_submission_report(self):
        response = self.client.get(
            f'/api/reports/forms/{self.form.id}/submissions/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        answer = response.data[0]['answers']

        self.assertIn('Name', answer)
        self.assertIn('Age', answer)
        self.assertIn('Color', answer)
        self.assertIn('Sport', answer)

    def test_form_aggregation(self):
        response = self.client.get(
            f'/api/reports/forms/{self.form.id}/aggregates/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

        number_report = next(
            item for item in response.data
            if item['question'] == 'Age'
        )

        self.assertEqual(number_report['total_answers'], 2)
        self.assertEqual(
            float(number_report['aggregation']['average']),
            37.5
        )
        self.assertEqual(
            float(number_report['aggregation']['minimum']),
            25
        )
        self.assertEqual(
            float(number_report['aggregation']['maximum']),
            50
        )

        select_report = next(
            item for item in response.data
            if item['question'] == 'Color'
        )

        self.assertEqual(
            select_report['aggregation']['Red'],
            1
        )
        self.assertEqual(
            select_report['aggregation']['Blue'],
            1
        )

        checkbox_report = next(
            item for item in response.data
            if item['question'] == 'Sport'
        )

        self.assertEqual(
            checkbox_report['aggregation']['Football'],
            2
        )
        self.assertEqual(
            checkbox_report['aggregation']['Table Tennis'],
            2
        )

    def test_process_report(self):
        response = self.client.get(
            f'/api/reports/process/{self.process.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['process_id'], self.process.id)
        self.assertEqual(response.data['title'], 'Test Process')
        self.assertEqual(response.data['response_count'], 1)
        self.assertEqual(response.data['visit_count'], 1)

    def test_user_only_see_own_reports(self):
        self.client.force_authenticate(
            user=self.other_user
        )

        response = self.client.get(
            f'/api/reports/forms/{self.form.id}/'
        )

        self.assertEqual(response.status_code, 404)

        response = self.client.get(
            f'/api/reports/process/{self.process.id}/'
        )

        self.assertEqual(response.status_code, 404)

    def test_scheduled_report_command(self):
        old_time = timezone.now() - timedelta(days=2)

        ScheduledReport.objects.filter(
            id=self.scheduled_report.id
        ).update(
            updated_at=old_time
        )

        with patch(
            'reports.management.commands.send_scheduled_reports.send_mail'
        ) as mock_send_mail:

            call_command('send_scheduled_reports')

            mock_send_mail.assert_called_once()

            args = mock_send_mail.call_args[0]

            self.assertIn(
                'گزارش دوره‌ای',
                args[0]
            )
            self.assertIn(
                'Test Form',
                args[1]
            )
            self.assertEqual(
                args[3],
                ['test@example.com']
            )

        self.scheduled_report.refresh_from_db()

        self.assertGreater(
            self.scheduled_report.updated_at,
            old_time
        )