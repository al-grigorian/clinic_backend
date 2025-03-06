from rest_framework import permissions
import redis
from django.conf import settings
from .serializers import * 
from .models import * 

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)