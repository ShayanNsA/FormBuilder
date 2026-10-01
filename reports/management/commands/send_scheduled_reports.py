from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone

from form.models import Form
from process.models import Process
from reports.models import ScheduledReport
from reports.services import get_form_report, get_process_report

class Command(BaseCommand):

    def handle(self, *args, **options):

        now = timezone.now()

        reports = ScheduledReport.objects.select_related('user')

        for report in reports:

            should_send = False

            if report.frequency == 'daily':
                should_send = now - report.updated_at >= timedelta(days=1)

            elif report.frequency == 'weekly':
                should_send = now - report.updated_at >= timedelta(days=7)

            elif report.frequency == 'monthly':
                should_send = now - report.updated_at >= timedelta(days=30)

            if not should_send:
                continue

            message = ""

            if report.report_type == 'form':

                forms = Form.objects.filter(
                    user=report.user,
                    is_deleted=False
                )

                message = "گزارش فرم‌ها\n\n"

                for form in forms:

                    data = get_form_report(form)

                    message += (
                        f"فرم: {data['title']}\n"
                        f"تعداد بازدید: {data['visit_count']}\n"
                        f"تعداد پاسخ: {data['submission_count']}\n\n"
                    )

            elif report.report_type == 'process':

                processes = Process.objects.filter(
                    user=report.user,
                    is_deleted=False
                )

                message = "گزارش فرایندها\n\n"

                for process in processes:
                    data = get_process_report(process)

                    message += (
                        f"فرایند: {data['title']}\n"
                        f"تعداد بازدید: {data['visit_count']}\n"
                        f"تعداد پاسخ: {data['response_count']}\n\n"
                    )

            send_mail(
                f"گزارش دوره‌ای {report.get_report_type_display()}",
                message,
                None,
                [report.user.email],
            )

            report.updated_at = now
            report.save(update_fields=['updated_at'])

            self.stdout.write(
                self.style.SUCCESS(
                    f"Report sent to {report.user.email}"
                )
            )