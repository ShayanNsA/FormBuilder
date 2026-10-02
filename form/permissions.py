import jwt
from django.conf import settings
from rest_framework import permissions

class CanAccessFormOrProcess(permissions.BasePermission):
    message = "شما اجازه دسترسی به این فرم را ندارید."

    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
            
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False    
        token = auth_header.split(' ')[1]
        
        try:
            #decode token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            #token belong to form
            if payload.get('token_type') == 'form_access' and str(payload.get('form_id')) == str(obj.id):
                return True
                
            #token belongs to parent process
            if payload.get('token_type') == 'process_access':
                process_id = payload.get('process_id')
                form_in_process = obj.step_in_process.filter(process_id=process_id).exists()
                if form_in_process:
                    return True

        except jwt.ExpiredSignatureError:
            self.message = "توکن منقضی شده است."
        except jwt.InvalidTokenError:
            self.message = "توکن نامعتبر است."
            
        return False