from django.shortcuts import render
from rest_framework.response import Response 
from django.shortcuts import get_object_or_404 
from rest_framework import status 
from .models import * 
from rest_framework.decorators import api_view
import datetime
from minio import Minio
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError

# Create your views here.
