from rest_framework import serializers
from form.models import Form,Category,Question
from submission.constants import QuestionCategory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','title','description','created_at','updated_at']
        read_only_fields=['id','created_at','updated_at']

class QuestionSerializer(serializers.ModelSerializer):    
    class Meta:
        model=Question
        fields=['id','form','title','question_type','is_required','order','question_options','created_at','updated_at']
        read_only_fields=['id','created_at','updated_at']

    def validate(self, data):
        question_type = data.get('question_type')
        question_options = data.get('question_options', [])

        if question_type in QuestionCategory.NEEDS_OPTIONS and not question_options:
            raise serializers.ValidationError({
                "question_options": "برای سوالات چندگزینه‌ای یا کشویی، باید حتماً گزینه‌ها را وارد کنید!"
            })
        #if it is text ,make question_options empty
        if question_type not in QuestionCategory.NEEDS_OPTIONS:
            data['question_options'] = []
            
        return data

class FormSerializer(serializers.ModelSerializer):

    #when read a form all questions are shown by order
    questions=QuestionSerializer(many=True,read_only=True)  
    #show all categories characteristics
    categories_details=CategorySerializer(source='categories',many=True,read_only=True)

    class Meta:
        model = Form
        fields = [
            'id', 'user', 'categories', 'categories_details', 'title', 'description', 
            'slug', 'is_public', 'password', 'is_deleted', 'created_at', 
            'updated_at', 'questions'
        ]
        read_only_fields = ['id','user', 'slug', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    #make new  password   hash 
    def create(self, validated_data):
        #extract special data
        password = validated_data.pop('password', None)
        categories = validated_data.pop('categories', [])
        #create a new form
        form = Form.objects.create(**validated_data)
        #hash password
        if password:
            form.set_password(password)
            form.save()
        #set categories    
        if categories:
            form.categories.set(categories)
            
        return form
    #update 
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



