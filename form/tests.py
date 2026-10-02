from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from form.models import Category, Form, Question

User = get_user_model()

class CategoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='shiva_test', 
            password='secret-0a5d4c8e',
            email='shiva_test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(
            title='دسته‌بندی اولیه',
            description='این یک دسته‌بندی تستی است.',
            user=self.user
        )
        self.list_url = '/api/form/categories/'
        self.detail_url = f'/api/form/categories/{self.category.pk}/'

    def test_get_category_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_category(self):
        data = {
            'title': 'دسته‌بندی جدید',
            'description': 'توضیحات دسته‌بندی جدید'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2) 
        self.assertEqual(Category.objects.get(id=response.data['id']).title, 'دسته‌بندی جدید')

    def test_update_category(self):
        data = {
            'title': 'عنوان ویرایش شده',
            'description': 'توضیحات ویرایش شده'
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.title, 'عنوان ویرایش شده')

    def test_delete_category(self):
       
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0) 


class FormAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_q', email='test_q@example.com', password='testpassword123')
        self.client.force_authenticate(user=self.user)
    
        self.category = Category.objects.create(
            user=self.user,
            title='دسته بندی تست'
        )
        self.form = Form.objects.create(
            user=self.user,
            title='فرم نظرسنجی اولیه',
            description='توضیحات فرم تستی',
            is_public=True
        )
        self.form.categories.add(self.category)

    def test_create_form(self):
        url = '/api/form/forms/' 
        data = {
            "title": "فرم تماس با ما",
            "description": "لطفا اطلاعات خود را وارد کنید",
            "is_public": True,
            "categories": [self.category.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Form.objects.count(), 2)
        self.assertEqual(response.data['title'], "فرم تماس با ما")

    def test_get_form_list(self):
        url = '/api/form/forms/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.form.title)

    def test_update_form(self):
        url = f'/api/form/forms/{self.form.id}/'
        data = {
            "title": "عنوان آپدیت شده فرم"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form.refresh_from_db()
        self.assertEqual(self.form.title, "عنوان آپدیت شده فرم")

    def test_delete_form_soft(self):
        url = f'/api/form/forms/{self.form.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
      
        self.form.refresh_from_db()
        self.assertTrue(self.form.is_deleted)


class QuestionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_q', email='test_q@example.com', password='testpassword123')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(title='Test Category Q', user=self.user)
      
        self.form = Form.objects.create(
            title='Test Form for Questions',
            user=self.user
        )
    
        self.question = Question.objects.create(
            form=self.form,
            title='What is your name?',
            question_type='text', 
            is_required=True
        )

    def test_create_question(self):
        url = reverse('form:question-list-create', kwargs={'form_id': self.form.id})
        data = {
            'title': 'How old are you?',
            'question_type': 'text', 
            'is_required': False,
            'form': self.form.id 
        }
        
        response = self.client.post(url, data, format='json')
        
        if response.status_code == 400:
            print(f"\n خروجی خطای CREATE: {response.data}\n")
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)

    def test_get_question_list(self):
        url = reverse('form:question-list-create', kwargs={'form_id': self.form.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_question(self):
        url = reverse('form:question-edit-delete', kwargs={'pk': self.question.id})
        data = {
            'title': 'Updated Question Title?',
            'question_type': 'text',
            'is_required': True,
            'form': self.form.id 
        }
        
        response = self.client.put(url, data, format='json')
        
        if response.status_code == 400:
            print(f"\n خروجی خطای UPDATE: {response.data}\n")
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, 'Updated Question Title?')

    def test_delete_question(self):
        url = reverse('form:question-edit-delete', kwargs={'pk': self.question.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 0)

    def test_question_permission_denied_for_other_user(self):
        hacker_user = User.objects.create_user(username='hacker_q', email='hacker_q@example.com', password='hackerpassword')
        self.client.force_authenticate(user=hacker_user)
        
        url = reverse('form:question-edit-delete', kwargs={'pk': self.question.id})
        response = self.client.delete(url)
        
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])