from django.db import models
from django.db.models import Max
from django.contrib.auth.hashers import make_password,check_password





class Process(models.Model):

    PROCESS_TYPES = (
            ('linear',  'step_by_step'),
            ('non_linear', 'flexible'),
            
        )
    user=models.ForeignKey('user.Usser',on_delete=models.CASCADE,related_name="created_process",verbose_name="process_creator")
    categories=models.ManyToManyField('form.Category',blank=True,related_name="processes",verbose_name="process_category")

    title=models.CharField(max_length=250,verbose_name="process_title")
    descriptin=models.TextField(max_length=500,blank=True,null=True,verbose_name="process_description")

    process_type=models.CharField(max_length=20,choices=PROCESS_TYPES)

    is_public=models.BooleanField(default=True,verbose_name="is_process_public?")
    
    password=models.CharField(max_length=128,blank=True,null=True,verbose_name="process_password")
    
    is_deleted=models.BooleanField(default=False,verbose_name="is_process_deleted?")

    created_at=models.DateTimeField(auto_now_add=True,verbose_name="creation_date")
    updated_at=models.DateTimeField(auto_now=True,verbose_name="update_date")

    #this method get password and save hash password in database
    def set_password(self,raw_password):
        self.password=make_password(raw_password)
    #this method checks if password equals hash password
    def check_password(self,raw_password):
        return check_password(raw_password,self.password)
    class Meta:
        verbose_name="process"
        verbose_name_plural="processes"
        ordering=['-created_at']
    
    def __str__(self):
        return f"{self.title} process is created by {self.user.username}"  

class ProcessStep(models.Model):
    process=models.ForeignKey(Process,on_delete=models.CASCADE,related_name="steps",verbose_name="process")    
    form=models.ForeignKey('form.Form',on_delete=models.CASCADE,related_name="step_in_process",verbose_name="related_form")
    step_order=models.PositiveIntegerField(blank=True,null=True,verbose_name="process_step")

    class Meta:
        verbose_name="process_step"
        verbose_name_plural="process_steps"
        ordering=['process','step_order']
        constraints = [
            models.UniqueConstraint(fields=['process', 'step_order'], name='unique_process_step_order'),
            models.UniqueConstraint(fields=['process', 'form'],name='unique_form_process'),
        ]        

    def save(self, *args, **kwargs):
       
        if self.step_order is None:
            aggregate_result = ProcessStep.objects.filter(process=self.process).aggregate(Max('step_order'))
            max_order = aggregate_result['step_order__max']
            
            if max_order is not None:
                self.step_order = max_order + 1  
            else:
                self.step_order = 1  
                
        super(ProcessStep, self).save(*args, **kwargs)


    def __str__(self):
        return f"form {self.form.title} is step:{self.step_order} of process {self.process.title}"
