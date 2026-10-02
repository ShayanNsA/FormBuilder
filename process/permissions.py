import jwt
from django.conf import settings
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
#this class check if user has tocken to access
class HasProcessTokenPermission(permissions.BasePermission):
    message = "شما توکن دسترسی معتبر برای این فرآیند را ندارید."

    def has_permission(self, request, view):
        #extract auth from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1]
        
        try:
            #decode tocken with secreet_key of project
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("توکن شما منقضی شده است. لطفاً دوباره وارد شوید.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("توکن شما نامعتبر است.")
        #check if tocken belongs to this process
        process_id_from_url = view.kwargs.get('process_id')
        if not process_id_from_url or payload.get('process_id') != process_id_from_url:
            self.message = "این توکن برای فرآیند دیگری صادر شده است."
            return False
        
        request.process_access_payload = payload
        return True