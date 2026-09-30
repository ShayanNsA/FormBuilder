from django.db import models
from django.db.models import Max
from django.contrib.auth.hashers import make_password,check_password
from django.utils.text import slugify

# Create your models here.




#this class depicts category entity
class Category(models.Model):

    #determin user creates category
    user=models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='categories',verbose_name='category_creator')
    
    title=models.CharField(max_length=250,verbose_name="category_title")
    descriptin=models.TextField(max_length=500,blank=True,null=True,verbose_name="category_description")

    created_at=models.DateTimeField(auto_now_add=True,verbose_name="creation_date")
    updated_at=models.DateTimeField(auto_now=True,verbose_name="update_date")

    class Meta:
        verbose_name="category"
        verbose_name_plural="categories"
        ordering=['-created_at']

    def __str__(self):
        return f"{self.title} category is created by {self.user.username}"  
    
class Form(models.Model):    
    #determin user creates form
    user=models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='forms',verbose_name='form_creator')

    #determine this form belongs to which category but it is nullable
    categories=models.ManyToManyField(Category,blank=True,related_name='forms',verbose_name='registered_category')    
    title=models.CharField(max_length=250,verbose_name="form_title")

    descriptin=models.TextField(max_length=500,blank=True,null=True,verbose_name="form_description")
    
    slug = models.SlugField(max_length=255, unique=True,allow_unicode=True,blank=True,verbose_name="slug")
    is_public=models.BooleanField(default=True,verbose_name="is_form_public?")

    password=models.CharField(max_length=128,blank=True,null=True,verbose_name="form_password")

    is_deleted=models.BooleanField(default=False,verbose_name="is_form_deleted?")

    created_at=models.DateTimeField(auto_now_add=True,verbose_name="creation_date")
    updated_at=models.DateTimeField(auto_now=True,verbose_name="update_date")

    #this method get password and save hash password in database
    def set_password(self,raw_password):
        self.password=make_password(raw_password)

    #this method checks if password equals hash password
    def check_password(self,raw_password):
        return check_password(raw_password,self.password)
       
    def save(self,*args,**kwargs):
        #if slug is empty
        if not self.slug:
           self.slug=slugify(self.title,allow_unicode=True)
        super(Form,self).save(*args,**kwargs)    
    
    class Meta:
        verbose_name="form"
        verbose_name_plural="forms"
        ordering=['-created_at']

    def __str__(self):
        return f"{self.title} form is created by {self.user.username}"  

class Question(models.Model):
    
    
    QUESTION_TYPES = (
        ('text',  'short_text'),
        ('textarea', 'long_text'),
        ('radio','single_choice' ),
        ('checkbox', 'multi_choices'),
        ('dropdown','dropdown' ),
    )

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions', verbose_name="related_form")
    title = models.CharField(max_length=500, verbose_name="question_text")
    question_type=models.CharField(max_length=20,choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True, verbose_name="is_response_required?")
    
    order = models.PositiveIntegerField(blank=True,null=True, verbose_name="depiction_order")

    question_options = models.JSONField(
        default=list, 
        blank=True, 
        null=True, 
        verbose_name="options",
        help_text="options list for multi_choices questions "
    )

    created_at=models.DateTimeField(auto_now_add=True,verbose_name="creation_date")
    updated_at=models.DateTimeField(auto_now=True,verbose_name="update_date")

    class Meta:
        verbose_name = "question"
        verbose_name_plural = "questions"
        ordering = ['order', 'created_at'] 
        constraints = [models.UniqueConstraint(fields=['form', 'order'], name='unique_question_order_per_form'),]

    def save(self, *args, **kwargs):
        if self.order is None:
            aggregate_result = Question.objects.filter(form=self.form).aggregate(Max('order'))
            max_order = aggregate_result['order__max']
            
            if max_order is not None:
                self.order = max_order + 1
            else:
                self.order = 1
                
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.form.title} | {self.title}"

