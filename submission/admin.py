from django.contrib import admin
from .models import Answer, FormSubmission, ProcessExecution


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    can_delete = False
    readonly_fields = ("question", "value_text", "value_number", "value_json")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ProcessExecution)
class ProcessExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "process", "user", "status", "current_step_order", "started_at")
    list_filter = ("status",)
    raw_id_fields = ("process", "user")
    date_hierarchy = "started_at"


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "form", "user", "process_execution", "is_reviewed", "submitted_at")
    list_filter = ("is_reviewed",)
    raw_id_fields = ("form", "user", "process_execution")
    date_hierarchy = "submitted_at"
    inlines = [AnswerInline]

