from django.contrib import admin

from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns =[
    path('admin/', admin.site.urls),
    path('api/reports/', include('reports.urls')),
    path('api/submission/', include('submission.urls')),
    path('api/form/',include('form.urls')),
    path('api/process/',include('process.urls')),

    path("api/accounts/", include("user.urls")),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema'),name='swagger-ui'),
]
