from django.urls import path
from . import views

app_name = "frontend"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("forms/", views.forms_page, name="forms"),
    path("forms/builder/", views.form_builder, name="form-builder"),
    path("processes/", views.processes_page, name="processes"),
    path("processes/builder/", views.process_builder, name="process-builder"),
    path("f/<slug:slug>/", views.public_form, name="public-form"),
    path("reports/", views.reports_page, name="reports"),
    path("profile/", views.profile_page, name="profile"),
]
