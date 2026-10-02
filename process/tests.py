from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from form.models import Category, Form
from process.models import Process, ProcessStep
from submission.constants import ProcessType
from rest_framework.test import APIClient
from django.contrib.auth.hashers import make_password

User = get_user_model()

class ProcessAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shiva_test',
            email='shiva@example.com',
            password='strongpassword123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.process_data = {
            'title': 'فرآیند ثبت نام ویزا',
            'description': 'تست ساخت فرآیند جدید',
            'process_type': 'linear', 
        }

    def test_create_process(self):
        url = reverse('process:process-list-create')
        response = self.client.post(url, self.process_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Process.objects.count(), 1)
        self.assertEqual(Process.objects.first().user, self.user)

    def test_soft_delete_process(self):
        process = Process.objects.create(
            title='فرآیند موقت برای حذف',
            user=self.user,
            process_type='linear' 
        )
        url = reverse('process:process-edit-delete', kwargs={'pk': process.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        process.refresh_from_db()
        self.assertTrue(process.is_deleted)
        
class ProcessAccessAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shiva_access',
            email='access@example.com',
            password='password123'
        )
        self.client = APIClient()
    
        self.public_process = Process.objects.create(
            title="فرآیند عمومی تابستانه",
            user=self.user,
            process_type='linear',
            is_public=True
        )
        
        self.secret_process = Process.objects.create(
            title="فرآیند محرمانه شرکت",
            user=self.user,
            process_type='linear', 
            is_public=False,
            password=make_password('supersecret123') 
        )

    def test_public_access(self):
      
        url = reverse('process:check-process_access', kwargs={'process_id': self.public_process.pk})
        response = self.client.post(url)
        
        if response.status_code == status.HTTP_403_FORBIDDEN:
             print("\n Access Error Details:", response.data)
             
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       

    def test_secret_access_denied(self):
      
        url = reverse('process:check-process_access', kwargs={'process_id': self.secret_process.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ProcessStepAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shiva_step',
            email='step@example.com',
            password='password123'
        )
        self.process = Process.objects.create(
            title="فرآیند دارای چند مرحله",
            user=self.user,
            process_type='linear' 
        )
        self.form1 = Form.objects.create(title="فرم اول", user=self.user)
        self.form2 = Form.objects.create(title="فرم دوم", user=self.user)

    def test_auto_ordering_steps(self):
        step1 = ProcessStep.objects.create(process=self.process, form=self.form1)
        step2 = ProcessStep.objects.create(process=self.process, form=self.form2)
        
        self.assertEqual(step1.step_order, 1)
        self.assertEqual(step2.step_order, 2)
        self.assertTrue(step2.step_order > step1.step_order)