from decimal import Decimal
from rest_framework import serializers
from form.models import Form
from process.models import Process
from . import services
from .models import Answer, FormSubmission, ProcessExecution


class AnswerInputSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    value = serializers.JSONField(allow_null=True)


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.question_text", read_only=True)
    question_type = serializers.CharField(source="question.question_type", read_only=True)
    value = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ["id", "question", "question_text", "question_type", "value"]

    def get_value(self, obj):
        value = obj.value
        if isinstance(value, Decimal):
            return int(value) if value == value.to_integral_value() else float(value)
        return value


class FormSubmissionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = FormSubmission
        fields = [
            "id",
            "form",
            "process_execution",
            "user",
            "submitter_ip",
            "submitted_at",
            "is_reviewed",
            "answers",
        ]
        read_only_fields = fields


class FormSubmissionCreateSerializer(serializers.Serializer):
    form = serializers.PrimaryKeyRelatedField(
        queryset=Form.objects.filter(is_deleted=False)
    )
    process_execution = serializers.PrimaryKeyRelatedField(
        queryset=ProcessExecution.objects.select_related("process"),
        required=False,
        allow_null=True,
    )
    answers = AnswerInputSerializer(many=True)

    def validate_process_execution(self, execution):
        if execution is not None and execution.user_id != self.context["request"].user.id:
            raise serializers.ValidationError("این اجرا متعلق به شما نیست.")
        return execution

    def validate(self, attrs):
        attrs["prepared_answers"] = services.validate_answers(
            attrs["form"], attrs["answers"]
        )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        return services.create_submission(
            form=validated_data["form"],
            user=request.user,
            ip=services.get_client_ip(request),
            prepared_answers=validated_data["prepared_answers"],
            execution=validated_data.get("process_execution"),
        )


class ProcessExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessExecution
        fields = [
            "id",
            "process",
            "user",
            "status",
            "current_step_order",
            "started_at",
            "completed_at",
        ]
        read_only_fields = fields


class ProcessExecutionCreateSerializer(serializers.Serializer):
    process = serializers.PrimaryKeyRelatedField(
        queryset=Process.objects.filter(is_deleted=False)
    )

    def create(self, validated_data):
        return services.start_execution(
            process=validated_data["process"],
            user=self.context["request"].user,
        )

