from django.db import models
from django.db.models import Q
from django.conf import settings


class ExecutionStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", "در حال تکمیل"
    COMPLETED = "completed", "تکمیل شده"


class ProcessExecution(models.Model):
    process = models.ForeignKey(
        "process.Process",
        on_delete=models.CASCADE,
        related_name="executions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="process_executions",
    )
    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.IN_PROGRESS,
    )
    current_step_order = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["process", "user"],
                condition=Q(status="in_progress"),
                name="uniq_active_execution_per_user_process",
            ),
        ]

    def __str__(self):
        return f"Execution #{self.pk} of process {self.process_id}"


class FormSubmission(models.Model):
    form = models.ForeignKey(
        "form.Form",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    process_execution = models.ForeignKey(
        ProcessExecution,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="submissions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="form_submissions"
    )
    submitter_ip = models.GenericIPAddressField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["form", "-submitted_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["process_execution", "form"],
                condition=Q(process_execution__isnull=False),
                name="uniq_form_per_process_execution",
            ),
        ]

    def __str__(self):
        return f"Submission #{self.pk} of form {self.form_id}"


class Answer(models.Model):
    form_submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        "form.Question",
        on_delete=models.CASCADE,
        related_name="answers",
    )
    value_text = models.TextField(null=True, blank=True)
    value_number = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        blank=True,
    )
    value_json = models.JSONField(null=True, blank=True)

    class Meta:
        constraints = [
            # only one answer for each question in a form submission
            models.UniqueConstraint(
                fields=["form_submission", "question"],
                name="uniq_answer_per_question_in_submission",
            ),
            # only one of these three fields should have value
            models.CheckConstraint(
                condition=(
                    Q(
                        value_text__isnull=False,
                        value_number__isnull=True,
                        value_json__isnull=True,
                    )
                    | Q(
                        value_text__isnull=True,
                        value_number__isnull=False,
                        value_json__isnull=True,
                    )
                    | Q(
                    value_text__isnull=True,
                    value_number__isnull=True,
                    value_json__isnull=False,
                    )
                ),
                name="answer_exactly_one_value",
            ),
        ]

    def __str__(self):
        return f"Answer #{self.pk} to question {self.question_id}"

    # to get answers easily without any if/else later.
    @property
    def value(self):
        if self.value_text is not None:
            return self.value_text
        if self.value_number is not None:
            return self.value_number
        return self.value_json

