from rest_framework import serializers

from .models import ScheduledReport, VisitLogs

class ScheduledReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScheduledReport
        fields = [
            'id',
            'user',
            'report_type',
            'frequency',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
        ]

class VisitLogsSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisitLogs
        fields = [
            'id',
            'user',
            'content_type',
            'object_id',
            'visitor_ip',
            'visited_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'visited_at'
        ]

class FormReportSerializer(serializers.Serializer):

    form_id = serializers.IntegerField()
    title = serializers.CharField()
    submission_count = serializers.IntegerField()
    visit_count = serializers.IntegerField()

class ProcessReportSerializer(serializers.Serializer):

    process_id = serializers.IntegerField()
    title = serializers.CharField()
    response_count = serializers.IntegerField()
    visit_count = serializers.IntegerField()

class FormSubmissionReportSerializer(serializers.Serializer):

    submission_id = serializers.IntegerField()
    submitted_at = serializers.DateTimeField()
    answers = serializers.DictField()

class QuestionAggregationSerializer(serializers.Serializer):

    question_id = serializers.IntegerField()
    question = serializers.CharField()
    question_type = serializers.CharField()
    total_answers = serializers.IntegerField()
    aggregation = serializers.DictField()