from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class ScheduledReport(models.Model):
    report_choices =  (
        ('form', 'form'),
        ('process', 'process'),
    )
    frequency_choices = (
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    )
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='scheduled_reports')
    report_type = models.CharField(choices=report_choices, max_length=10, default='form')
    frequency = models.CharField(choices=frequency_choices, max_length=10, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.get_frequency_display()}"

class VisitLogs(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey('user.User', on_delete=models.SET_NULL, related_name='visit_logs', null=True, blank=True)
    visitor_ip = models.GenericIPAddressField()
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit to {self.content_object} at {self.visited_at}"