from django.contrib.contenttypes.models import ContentType

from .models import VisitLogs
from submission.models import FormSubmission

def log_visit(request, obj):

    content_type = ContentType.objects.get_for_model(obj)

    VisitLogs.objects.create(
        content_type=content_type,
        object_id=obj.id,
        user=request.user if request.user.is_authenticated else None,
        visitor_ip=request.META.get('REMOTE_ADDR'),
    )

def get_form_report(form):

    submission_count = FormSubmission.objects.filter(
        form=form,
    ).count()

    content_type = ContentType.objects.get_for_model(form)

    visit_count = VisitLogs.objects.filter(
        content_type=content_type,
        object_id=form.id,
    ).count()

    return {
        'form_id': form.id,
        'title': form.title,
        'submission_count': submission_count,
        'visit_count': visit_count,
    }

def get_process_report(process):

    response_count = FormSubmission.objects.filter(
        process_execution__process=process,
    ).count()

    content_type = ContentType.objects.get_for_model(process)

    visit_count = VisitLogs.objects.filter(
        content_type=content_type,
        object_id=process.id,
    ).count()

    return {
        'process_id': process.id,
        'title': process.title,
        'response_count': response_count,
        'visit_count': visit_count,
    }