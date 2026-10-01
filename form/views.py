from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from form.models import Category,Form,Question
from form.serializers import CategorySerializer,FormSerializer,QuestionSerializer


class CategoryListCreate(APIView):

    permission_classes=[IsAuthenticated]

    #show the categories made by user send request
    def get(self,request):
        categories=Category.objects.filter(user=request.user)
        serializer=CategorySerializer(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    #make a new category
    def post(self,request):
        serializer=CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CategoryEditDelete(APIView):

    permission_classes=[IsAuthenticated]

    def get_object(self,pk,user):
        return get_object_or_404(Category,pk=pk,user=user)

    # show category by id
    def get(self,request,pk):
        category = self.get_object(pk, request.user)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #edit category 
    def put(self,request,pk):
        category=self.get_object(pk,request.user)
        serializer=CategorySerializer(category,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #delete category
    def delete(self,request,pk):
        category=self.get_object(pk,request.user)
        category.delete()
        return Response({"message":"دسته بندی مدنظر حذف گردید!"}, status=status.HTTP_204_NO_CONTENT)


class FormListCreate(APIView):
    permission_classes=[IsAuthenticated]

    #show list of forms made by user send request
    def get(self,request):
        forms=Form.objects.filter(user=request.user,is_deleted=False)
        serializer=FormSerializer(forms,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    #make a new form
    def post(self,request):
        serializer=FormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class FormEditDelete(APIView):
        permission_classes=[IsAuthenticated]
     
        def get_object(self,pk,user):
             return get_object_or_404(Form,pk=pk,user=user,is_deleted=False)   

        # show form by id
        def get(self,request,pk):
            form= self.get_object(pk, request.user)
            serializer = FormSerializer(form)
            return Response(serializer.data, status=status.HTTP_200_OK)

        #edit category 
        def put(self,request,pk):
            form=self.get_object(pk,request.user)
            serializer=FormSerializer(form,data=request.data,partial=True)
    
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            
        #delete category
        def delete(self,request,pk):
            form=self.get_object(pk,request.user)
            #soft delete
            #form get keeps in database for some reports but is_deleted shows user delete this form
            form.is_deleted=True
            form.save()
            return Response({"message":"فرم مدنظر حذف گردید!"}, status=status.HTTP_204_NO_CONTENT)


class QuestionListCreate(APIView):
    permission_classes=[IsAuthenticated]

    #check question belongs to this form and form not delete
    def get_form(self, form_id, user):
            return get_object_or_404(Form, pk=form_id, user=user, is_deleted=False)
    def get(self, request, form_id):    
        form = self.get_form(form_id, request.user)
        questions = Question.objects.filter(form=form)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #make a new question
    def post(self,request,form_id):

        form = self.get_form(form_id, request.user)
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(form=form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionEditDelete(APIView):
    permission_classes=[IsAuthenticated]
     
    def get_object(self,pk,user):
        question=get_object_or_404(Question,pk=pk)   
        if question.form.user!=user or question.form.is_deleted:
            return None
        return question

    
    # show question by id
    def get(self,request,pk):
        question= self.get_object(pk, request.user)
        if not question:
            return Response({"error": "کاربر گرامی اجازه مشاهده به این سؤال را ندارید"}, status=status.HTTP_403_FORBIDDEN)
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #edit question
    def put(self,request,pk):
        question=self.get_object(pk,request.user)
        if not question:
                    return Response({"error": "کاربر گرامی اجازه ویرایش به این سؤال را ندارید"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer=QuestionSerializer(question,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            
    #delete question
    def delete(self,request,pk):
        question=self.get_object(pk,request.user)
        if not question:
            return Response({"error": "کاربر گرامی اجازه حذف به این سؤال را ندارید"}, status=status.HTTP_403_FORBIDDEN)
                
        question.delete()
        return Response({"message":"سؤال مدنظر حذف گردید!"}, status=status.HTTP_204_NO_CONTENT)        