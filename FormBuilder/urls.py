from django.contrib import admin

from django.urls import path, include

urlpatterns =[
    path('admin/', admin.site.urls),
    path('api/reports/', include('reports.urls')),
    path('api/submission/', include('submission.urls')),
    path('api/form/',include('form.urls')),
    path('api/process/',include('process.urls')),
]
