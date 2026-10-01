from django.urls import path

from .views import (
    ScheduledReportView,
    VisitLogsView,
    FormReportView,
    FormSubmissionReportView,
    ProcessReportView,
    FormAggregationView,
)

urlpatterns = [
    path('scheduled-reports/', ScheduledReportView.as_view(), name='scheduled-reports'),
    path('visit-logs/', VisitLogsView.as_view(), name='visit-logs'),
    path('forms/<int:form_id>/', FormReportView.as_view(), name='form-report'),
    path('process/<int:process_id>/', ProcessReportView.as_view(), name='process-report'),
    path('forms/<int:form_id>/submissions/', FormSubmissionReportView.as_view(), name='form-submissions-report'),
    path('forms/<int:form_id>/aggregates/',FormAggregationView.as_view(), name='form-aggregation'),
]