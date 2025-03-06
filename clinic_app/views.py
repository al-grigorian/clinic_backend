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
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from datetime import timedelta
import redis

# Create your views here.

# session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

# GET - список всех врачей
@swagger_auto_schema(method='get', operation_summary="Получение списка всех врачей")
@api_view(['GET'])
def get_doctors(request, format=None):
    # Получаем всех врачей из базы данных
    doctors = Doctor.objects.all()

    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)


# GET - список всех пациентов
@swagger_auto_schema(method='get', operation_summary="Получение списка всех пациентов")
@api_view(['GET'])
def get_patients(request, format=None):
    # Получаем всех врачей из базы данных
    patients = Patient.objects.all()

    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)


# GET - список всех специальностей
@swagger_auto_schema(method='get', operation_summary="Получение списка всех специализаций")
@api_view(['GET'])
def get_specializations(request, format=None):
    # Получаем всех врачей из базы данных
    specializations = Specialization.objects.all()

    serializer = SpecializationSerializer(specializations, many=True)
    return Response(serializer.data)


# GET - список всех процедур
@swagger_auto_schema(method='get', operation_summary="Получение списка всех процедур")
@api_view(['GET'])
def get_procedures(request, format=None):
    # Получаем всех врачей из базы данных
    procedures = Procedure.objects.all()

    serializer = ProcedureSerializer(procedures, many=True)
    return Response(serializer.data)


# GET - список врачей, проводящих конкретную 
@swagger_auto_schema(method='get', operation_summary="Получение списка врачей, проводящих конкретную процедуру")
@api_view(['GET'])
def get_doctors_by_procedure(request, procedure_id, format=None):
    try:
        procedure = Procedure.objects.get(pk=procedure_id)
    except Procedure.DoesNotExist:
        return Response("Процедура не найдена.", status=status.HTTP_404_NOT_FOUND)

    # Получаем всех врачей, которые проводят эту процедуру
    doctors_procedures = DoctorsProcedures.objects.filter(procedure=procedure)
    doctors = [dp.doctor for dp in doctors_procedures]

    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)


# GET - список всех записей конкретного пациента
@swagger_auto_schema(method='get', operation_summary="Получение списка всех записей конкретного пациента")
@api_view(['GET'])
def get_records_by_patient(request, patient_id, format=None):
    try:
        patient = Patient.objects.get(pk=patient_id)
    except Patient.DoesNotExist:
        return Response("Пациент не найден.", status=status.HTTP_404_NOT_FOUND)

    # Получаем все записи, связанные с этим пациентом
    records = Record.objects.filter(patient=patient)

    serializer = RecordSerializer(records, many=True)
    return Response(serializer.data)


# GET - список всех записей конкретного врача
@swagger_auto_schema(method='get', operation_summary="Получение списка всех записей конкретного врача")
@api_view(['GET'])
def get_records_by_doctor(request, doctor_id, format=None):
    try:
        doctor = Doctor.objects.get(pk=doctor_id)
    except Doctor.DoesNotExist:
        return Response("Врач не найден.", status=status.HTTP_404_NOT_FOUND)

    # Получаем все записи, связанные с этим врачом
    records = Record.objects.filter(doctor=doctor)

    serializer = RecordSerializer(records, many=True)
    return Response(serializer.data)


# GET - список всех лечений конкретного пациента
@swagger_auto_schema(method='get', operation_summary="Получение списка всех лечений конкретного пациента")
@api_view(['GET'])
def get_treatments_by_patient(request, patient_id, format=None):
    try:
        patient = Patient.objects.get(pk=patient_id)
    except Patient.DoesNotExist:
        return Response("Пациент не найден.", status=status.HTTP_404_NOT_FOUND)

    # Получаем все лечения, связанные с этим пациентом
    treatments = Treatment.objects.filter(record__patient=patient).distinct()

    serializer = TreatmentSerializer(treatments, many=True)
    return Response(serializer.data)


# GET - список медикаментов, относящихся к конкретному лечению
@swagger_auto_schema(method='get', operation_summary="Получение списка медикаментов, относящихся к конкретному лечению")
@api_view(['GET'])
def get_medicaments_by_treatment(request, treatment_id, format=None):
    try:
        treatment = Treatment.objects.get(pk=treatment_id)
    except Treatment.DoesNotExist:
        return Response("Лечение не найдено.", status=status.HTTP_404_NOT_FOUND)

    # Получаем все медикаменты, связанные с этим лечением
    treatment_medicaments = TreatmentMedicament.objects.filter(treatment=treatment)
    medicaments = [tm.medicament for tm in treatment_medicaments]

    serializer = MedicamentSerializer(medicaments, many=True)
    return Response(serializer.data)


# PUT - изменение статуса записи врачом на "завершено"
@swagger_auto_schema(method='put', operation_summary="Изменение статуса записи врачом на 'завершено'")
@api_view(['PUT'])
def update_record_by_doctor(request, record_id):
    try:
        record = Record.objects.get(pk=record_id)
    except Record.DoesNotExist:
        return Response("Запись не найдена.", status=status.HTTP_404_NOT_FOUND)

    # Обновляем статус записи на "завершено"
    record.status = 6  # 6 - это статус "Завершено"

    # Устанавливаем время окончания как время начала + 1.5 часа
    if record.start_time:
        record.end_time = record.start_time + timedelta(hours=1.5)
    else:
        return Response("Время начала записи не указано.", status=status.HTTP_400_BAD_REQUEST)

    record.save()

    serializer = RecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)


# PUT - обновление статуса заявки админом на "Подтверждено"
@swagger_auto_schema(method='put', operation_summary="Обновление статуса заявки админом на 'Подтверждено'")
@api_view(['PUT'])
def update_record_by_admin(request, record_id):
    try:
        record = Record.objects.get(pk=record_id)
    except Record.DoesNotExist:
        return Response("Запись не найдена.", status=status.HTTP_404_NOT_FOUND)

    # Обновляем статус записи на "Подтверждено"
    record.status = 2  # 2 - это статус "Подтверждено"
    record.save()

    serializer = RecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)

"""
# POST - регистрация
@swagger_auto_schema(method='post', operation_summary="Регистрация")
@api_view(['POST'])
def register(request):

# POST - авторизация
@swagger_auto_schema(method='post', operation_summary="Регистрация")
@api_view(['POST'])
def login(request):

# POST - выход из профиля
@swagger_auto_schema(method='post', operation_summary="Выход из профиля")
@api_view(['POST'])
def logout
"""