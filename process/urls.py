from django.urls import path
from process import views

app_name='process'

urlpatterns=[
   
    path('processes/', views.ProcessListCreate.as_view(), name='process-list-create'),
    path('<int:pk>/', views.ProcessEditDelete.as_view(), name='process-edit-delete'),

     path('access/<int:process_id>/', views.ProcessAccess.as_view(), name='check-process_access'),
   
    path('<int:process_id>/steps/', views.ProcessStepListCreate.as_view(), name='step-list-create'),
    path('<int:process_id>/steps/<int:pk>/', views.ProcessStepEditDelete.as_view(), name='step-edit-delete'),

    
    path('<int:process_id>/verify-password/', views.VerifyPassword.as_view(), name='verify-password'),
]
