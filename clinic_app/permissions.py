from rest_framework import permissions
import redis
from django.conf import settings
from .serializers import * 
from .models import * 

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if "session_id" not in request.COOKIES:
            return False

        access_token = request.COOKIES["session_id"]
        print(request.COOKIES["session_id"])

        try:
            username = session_storage.get(access_token).decode('utf-8')
        except Exception as e:
            return False

        user = User.objects.filter(email=username).first()
        return user.is_admin

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        if "session_id" not in request.COOKIES:
            return False

        access_token = request.COOKIES["session_id"]
        print(request.COOKIES["session_id"])

        try:
            username = session_storage.get(access_token).decode('utf-8')
        except Exception as e:
            return False

        user = User.objects.filter(email=username).first()
        return user.is_doctor
    
class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        if "session_id" not in request.COOKIES:
            return False

        access_token = request.COOKIES["session_id"]
        print(request.COOKIES["session_id"])

        try:
            username = session_storage.get(access_token).decode('utf-8')
        except Exception as e:
            return False

        user = User.objects.filter(email=username).first()
        return user.is_patient
    
class IsAuth(permissions.BasePermission): 
    def has_permission(self, request, view): 
        # access_token = request.headers.get('Authorization') 
        access_token = request.COOKIES["session_id"]
        print('cheeeeck', access_token)
 
        if access_token is None: 
            return False 
 
        try: 
            user = session_storage.get(access_token).decode('utf-8') 
        except Exception as e: 
            return False 
 
        return True