from django.contrib import admin

from .models import ScheduledReport,VisitLogs

admin.site.register(ScheduledReport)
admin.site.register(VisitLogs)