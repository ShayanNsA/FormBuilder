from django.shortcuts import render

def home(request): return render(request, "frontend/home.html")
def login_page(request): return render(request, "frontend/auth.html", {"mode": "login"})
def register_page(request): return render(request, "frontend/auth.html", {"mode": "register"})
def dashboard(request): return render(request, "frontend/dashboard.html")
def forms_page(request): return render(request, "frontend/forms.html")
def form_builder(request): return render(request, "frontend/form_builder.html")
def processes_page(request): return render(request, "frontend/processes.html")
def process_builder(request): return render(request, "frontend/process_builder.html")
def public_form(request, slug): return render(request, "frontend/public_form.html", {"slug": slug})
def reports_page(request): return render(request, "frontend/reports.html")
def profile_page(request): return render(request, "frontend/profile.html")
