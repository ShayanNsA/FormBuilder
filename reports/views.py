from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Min, Max

from form.models import Form
from process.models import Process
from submission.models import FormSubmission, Answer
from submission.constants import QuestionCategory

from .models import ScheduledReport, VisitLogs
from .serializers import (
    ScheduledReportSerializer,
    VisitLogsSerializer,
    FormReportSerializer,
    ProcessReportSerializer,
    FormSubmissionReportSerializer,
    QuestionAggregationSerializer
)

from collections import Counter

from django.core.cache import cache

class ScheduledReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = ScheduledReport.objects.filter(user=request.user)

        serializer = ScheduledReportSerializer(reports, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = ScheduledReportSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class VisitLogsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = VisitLogs.objects.filter(user=request.user)

        serializer = VisitLogsSerializer(logs, many=True)

        return Response(serializer.data)

class FormReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, form_id):

        cache_key = f'form_report_{request.user.id}_{form_id}'

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        form = get_object_or_404(
            Form,
            id=form_id,
            user=request.user,
            is_deleted=False
        )

        content_type = ContentType.objects.get_for_model(Form)

        submission_count = form.submissions.count()

        visit_count = VisitLogs.objects.filter(
            content_type=content_type,
            object_id=form.id,
        ).count()

        data = {
            'form_id': form.id,
            'title': form.title,
            'submission_count': submission_count,
            'visit_count': visit_count,
        }

        serializer = FormReportSerializer(data)

        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        )

        return Response(serializer.data)

class FormSubmissionReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, form_id):

        cache_key = f'form_submission_report_{request.user.id}_{form_id}'

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        form = get_object_or_404(
            Form,
            id=form_id,
            user=request.user,
            is_deleted=False
        )

        submissions = FormSubmission.objects.filter(
            form=form
        ).prefetch_related('answers', 'answers__question')

        data = []

        for submission in submissions:

            answers = {}

            for answer in submission.answers.all():
                answers[answer.question.title] = answer.value

            data.append({
                'submission_id': submission.id,
                'submitted_at': submission.submitted_at,
                'answers': answers,
            })

        serializer = FormSubmissionReportSerializer(data, many=True)

        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        )

        return Response(serializer.data)

class FormAggregationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, form_id):

        cache_key = f'form_aggregation_{request.user.id}_{form_id}'

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        form = get_object_or_404(
            Form,
            id=form_id,
            user=request.user,
            is_deleted=False
        )

        questions = form.questions.all()

        data = []

        for question in questions:

            answers = Answer.objects.filter(
                question=question,
                form_submission__form=form,
            )

            total_answers = answers.count()

            aggregation = {}

            if question.question_type in QuestionCategory.NUMBER_TYPES:

                result = answers.aggregate(
                    average=Avg('value_number'),
                    minimum=Min('value_number'),
                    maximum=Max('value_number'),
                )

                aggregation = {
                    'average': result['average'],
                    'minimum': result['minimum'],
                    'maximum': result['maximum'],
                }

            elif question.question_type in (
                QuestionCategory.SINGLE_CHOICE_TYPES
                | QuestionCategory.MULTI_CHOICE_TYPES
            ):

                counter = Counter()

                for answer in answers:
                    value = answer.value

                    if isinstance(value, list):
                        counter.update(value)
                    else:
                        counter[value] += 1

                aggregation = dict(counter)

            data.append({
                'question_id': question.id,
                'question': question.title,
                'question_type': question.question_type,
                'total_answers': total_answers,
                'aggregation': aggregation,
            })

        serializer = QuestionAggregationSerializer(data, many=True)

        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        )

        return Response(serializer.data)

class ProcessReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, process_id):

        cache_key = f'process_report_{request.user.id}_{process_id}'

        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        process = get_object_or_404(
            Process,
            id=process_id,
            user=request.user,
            is_deleted=False
        )

        content_type = ContentType.objects.get_for_model(Process)

        response_count = FormSubmission.objects.filter(
            process_execution__process=process,
        ).count()

        visit_count = VisitLogs.objects.filter(
            content_type=content_type,
            object_id=process.id,
        ).count()

        data = {
            'process_id': process.id,
            'title': process.title,
            'response_count': response_count,
            'visit_count': visit_count,
        }

        serializer = ProcessReportSerializer(data)

        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        )

        return Response(serializer.data)