from django.db.models import Prefetch, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Answer, FormSubmission, ProcessExecution
from .serializers import (
    FormSubmissionCreateSerializer, FormSubmissionSerializer,
    ProcessExecutionCreateSerializer, ProcessExecutionSerializer,
)


def _int_param(request, name):
    value = request.query_params.get(name)
    if value is None:
        return None
    if not value.isdigit():
        raise ValidationError({name: "مقدار باید عدد صحیح باشد."})
    return int(value)


class ProcessExecutionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = ProcessExecution.objects.select_related("process").filter(
            Q(user=user) | Q(process__creator=user)
        )
        if self.action == "list":
            process_id = _int_param(self.request, "process")
            if process_id is not None:
                queryset = queryset.filter(process_id=process_id)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return ProcessExecutionCreateSerializer
        return ProcessExecutionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        execution = serializer.save()
        data = ProcessExecutionSerializer(
            execution, context=self.get_serializer_context()
        ).data
        return Response(data, status=status.HTTP_201_CREATED)


class FormSubmissionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = (
            FormSubmission.objects.select_related("form")
            .prefetch_related(
                Prefetch("answers", queryset=Answer.objects.select_related("question"))
            )
            .filter(Q(user=user) | Q(form__creator=user))
        )
        if self.action == "list":
            form_id = _int_param(self.request, "form")
            if form_id is not None:
                queryset = queryset.filter(form_id=form_id)
            execution_id = _int_param(self.request, "process_execution")
            if execution_id is not None:
                queryset = queryset.filter(process_execution_id=execution_id)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return FormSubmissionCreateSerializer
        return FormSubmissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()
        instance = self.get_queryset().get(pk=submission.pk)
        data = FormSubmissionSerializer(
            instance, context=self.get_serializer_context()
        ).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        submission = self.get_object()
        if submission.form.creator_id != request.user.id:
            raise PermissionDenied("فقط سازنده فرم می‌تواند پاسخ را بررسی کند.")
        if not submission.is_reviewed:
            submission.is_reviewed = True
            submission.save(update_fields=["is_reviewed"])
        return Response(self.get_serializer(submission).data)

