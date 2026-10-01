from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from process.models import Process,ProcessStep
from process.serializers import ProcessSerializer,ProcessStepSerializer


class ProcessListCreate(APIView):
    permission_classes=[IsAuthenticated]

    #show list of processes made by user send request
    def get(self,request):
        processes=Process.objects.filter(user=request.user,is_deleted=False)
        serializer=ProcessSerializer(processes,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    #make a new process
    def post(self,request):
        serializer=ProcessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class ProcessEditDelete(APIView):
        permission_classes=[IsAuthenticated]
     
        def get_object(self,pk,user):
             return get_object_or_404(Process,pk=pk,user=user,is_deleted=False)   

        # show Process by id
        def get(self,request,pk):
            process= self.get_object(pk, request.user)
            serializer =ProcessSerializer(process)
            return Response(serializer.data, status=status.HTTP_200_OK)

        #edit process
        def put(self,request,pk):
            process=self.get_object(pk,request.user)
            serializer=ProcessSerializer(process,data=request.data,partial=True)
    
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            
        #delete process
        def delete(self,request,pk):
            process=self.get_object(pk,request.user)
            #soft delete
            #form get keeps in database for some reports but is_deleted shows user delete this form
            process.is_deleted=True
            process.save()
            return Response({"message":"فرآیند مدنظر حذف گردید!"}, status=status.HTTP_204_NO_CONTENT)

class ProcessStepListCreate(APIView):
    
    permission_classes = [IsAuthenticated]

    #check if processstep belongs to a process
    def get_process(self, process_id, user):
        return get_object_or_404(Process, pk=process_id, user=user, is_deleted=False)

    def get(self, request, process_id):
        process = self.get_process(process_id, request.user)
        steps = ProcessStep.objects.filter(process=process)
        serializer = ProcessStepSerializer(steps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, process_id):
        process = self.get_process(process_id, request.user)
        serializer = ProcessStepSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(process=process)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessStepEditDelete(APIView):
  
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(ProcessStep, pk=pk, process__user=user, process__is_deleted=False)

    def get(self, request, pk):
        step = self.get_object(pk, request.user)
        serializer = ProcessStepSerializer(step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        step = self.get_object(pk, request.user)
        serializer = ProcessStepSerializer(step, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        step = self.get_object(pk, request.user)
        step.delete() 
        return Response({"message": "مرحله با موفقیت حذف شد."}, status=status.HTTP_204_NO_CONTENT)


