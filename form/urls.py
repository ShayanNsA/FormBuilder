from django.urls import path
from form import views

app_name='form'

urlpatterns=[
    path('categories/',views.CategoryListCreate.as_view(),name='category-list-create'),
    path('categories/<int:pk>/',views.CategoryEditDelete.as_view(), name='category-edit-delete'),

    path('forms/',views.FormListCreate.as_view(),name="form-list-create"),
    path('forms/<int:pk>/',views.FormEditDelete.as_view(),name="form-edit-delete"),
    path('<slug:slug>/access/',views.FormAccess.as_view(), name='check-form-access'),
     path('<slug:slug>/', views.FormGuestDetailView.as_view(), name='form-guest-detail'),
    
    path('forms/<int:form_id>/questions/',views.QuestionListCreate.as_view(),name="question-list-create"),
    path('questions/<int:pk>/',views.QuestionEditDelete.as_view(),name="question-edit-delete"),

]