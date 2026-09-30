from rest_framework import serializers
from process.models import Process,ProcessStep
from form.serializers import CategorySerializer
from submission.constants import ProcessType


class ProcessStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = ['id', 'process', 'form', 'step_order']
        read_only_fields = ['id','step_order']

class ProcessSerializer(serializers.ModelSerializer):
    #show steps of this process
    steps=ProcessStepSerializer(many=True,read_only=True)
    #show all categories characteristics
    categories_details=CategorySerializer(source='categories',many=True,read_only=True)
    class Meta:
        model = Process
        fields = ['id', 'user', 'categories','categories_details', 'title', 'description', 
                'process_type', 'is_public', 'password', 'is_deleted', 'created_at', 
                'updated_at','steps' ]
        read_only_fields = ['id','user', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
           
        }
    def validate_process_type(self, value):
        if value not in ProcessType.values:
            raise serializers.ValidationError("نوع فرآیند انتخاب شده نامعتبر است.")
        return value
    
    def create(self, validated_data):
        #seperate special datae
        categories = validated_data.pop('categories', [])
        password = validated_data.pop('password', None)
        #make a new process
        process = Process.objects.create(**validated_data)
        #hash password
        if password:
            process.set_password(password)
            process.save()
            
        #set categories
        if categories:
            process.categories.set(categories)
            
        return process

    def update(self, instance, validated_data):
        #extract new password and categories
        password = validated_data.pop('password', None)
        categories = validated_data.pop('categories', None)
        #hash new password
        if password:
            instance.set_password(password)
        #set categories
        if categories is not None:
            instance.categories.set(categories)         
        #update other fields by super method
        return super().update(instance, validated_data)