from django.shortcuts import render
from rest_framework.response import Response 
from django.shortcuts import get_object_or_404 
from rest_framework import status 
from .models import * 
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import datetime
from minio import Minio
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from datetime import timedelta
import redis
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
import uuid
from clinic_app.permissions import *
from django.db.models import Avg
from datetime import datetime
from drf_yasg import openapi
# Create your views here.

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


#########################################################################################################
# ------------------------------------------------- GET -------------------------------------------------
#########################################################################################################


# GET - список всех врачей
@swagger_auto_schema(
    tags=["GET-запросы"],
    method='get',
    operation_summary="Получение списка всех врачей",
    responses={200: DoctorSerializer(many=True)})
@api_view(['GET'])
def get_doctors(request, format=None):
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)


# GET - список всех процедур с фильтром
@swagger_auto_schema(
    tags=["GET-запросы"], 
    method='get', 
    operation_summary="Получение списка всех процедур с фильтром",
    manual_parameters=[
        openapi.Parameter(
            name='search',
            in_=openapi.IN_QUERY,
            description="Поиск по названию процедуры",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            name='min_price',
            in_=openapi.IN_QUERY,
            description="Минимальная цена",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            name='max_price',
            in_=openapi.IN_QUERY,
            description="Максимальная цена",
            type=openapi.TYPE_INTEGER
        )
    ],
    responses={200: ProcedureSerializer(many=True)})
@api_view(['GET'])
def get_procedures(request, format=None):
    search_query = request.GET.get('search', '')
    min_price = int(request.GET.get('min_price', 0))
    max_price = int(request.GET.get('max_price', 1000000))
    
    procedures = Procedure.objects.filter(name__icontains=search_query).filter(price__range=(min_price, max_price))

    serializer = ProcedureSerializer(procedures, many=True)
    return Response(serializer.data)


"""
# GET - получение доктора по ID
@swagger_auto_schema(tags=["GET-запросы"], method='get', operation_summary="Получение врача по ID")
@api_view(['GET'])
def get_doctor_by_id(request, doctor_id, format=None):
    try:
        doctor = Doctor.objects.get(pk=doctor_id)
    except Doctor.DoesNotExist:
        return Response("Врач не найден.", status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorSerializer(doctor)
    return Response(serializer.data)


# GET - получение процедуры по ID
@swagger_auto_schema(tags=["GET-запросы"], method='get', operation_summary="Получение процедуры по ID")
@api_view(['GET'])
def get_procedure_by_id(request, procedure_id, format=None):
    try:
        procedure = Procedure.objects.get(pk=procedure_id)
    except Procedure.DoesNotExist:
        return Response("Процедура не найдена.", status=status.HTTP_404_NOT_FOUND)

    serializer = ProcedureSerializer(procedure)
    return Response(serializer.data)


# GET - список всех пациентов
@swagger_auto_schema(tags=["GET-запросы"], method='get', operation_summary="Получение списка всех пациентов")
@api_view(['GET'])
def get_patients(request, format=None):
    # Получаем всех врачей из базы данных
    patients = Patient.objects.all()

    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)


# GET - список всех специальностей
@swagger_auto_schema(tags=["GET-запросы"], method='get', operation_summary="Получение списка всех специализаций")
@api_view(['GET'])
def get_specializations(request, format=None):
    # Получаем всех врачей из базы данных
    specializations = Specialization.objects.all()

    serializer = SpecializationSerializer(specializations, many=True)
    return Response(serializer.data)

"""


# GET - список всех записей со статусом "Ожидание подтверждения" для админа
@swagger_auto_schema(
    tags=["GET-запросы"],
    method='get',
    operation_summary="Получение админом списка всех записей со статусом 'Ожидание подтверждения'",
    responses={200: SimpleRecordSerializer(many=True)})
@api_view(['GET'])
def get_pending_records(request, format=None):
    # Получаем все записи со статусом "Ожидание подтверждения"
    pending_records = Record.objects.filter(status=1)

    serializer = SimpleRecordSerializer(pending_records, many=True)
    return Response(serializer.data)


# GET - список врачей, проводящих конкретную процедуру
@swagger_auto_schema(
    tags=["GET-запросы"], 
    method='get', 
    operation_summary="Получение списка врачей, проводящих конкретную процедуру",
    responses={200: DoctorSerializer(many=True)})
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


# GET - список всех записей пациента с фильтром по статусу, если статус не передан в параметре, по умолчанию выведет список записей со статусом 'Ожидание подтверждения' и 'Подтверждено'
@swagger_auto_schema(
    tags=["GET-запросы"], 
    method='get', 
    operation_summary=("Получение списка записей пациента с фильтром по статусу. " 
                       "Если статус не передан в параметре, выведет записи со статусом 'Ожидание подтверждения' (status=1) и 'Подтверждено' (status=2). "
                        "Список сортируется по полю status по возрастанию"),
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            description="Статус записи",
            type=openapi.TYPE_INTEGER,
            required=False
        )
    ],
    responses={
        200: SimpleRecordSerializer(many=True),
        400: "Bad Request - Пользователь не является пациентом",
        403: "Forbidden - Сессия не найдена",
        404: "Not Found - Пользователь не найден"
    }
)
@api_view(['GET'])
def get_records_by_patient(request, format=None):
    if "session_id" in request.COOKIES:
        ssid = request.COOKIES["session_id"]
    else:
        return HttpResponseForbidden('Сессия не найдена')

    try:
        email = session_storage.get(ssid).decode('utf-8')
        user = User.objects.get(email=email)
    except (User.DoesNotExist, AttributeError):
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_patient:
        return Response({"error": "Пользователь не пациент."}, status=status.HTTP_400_BAD_REQUEST)

    patient = Patient.objects.get(user=user)

    # Получаем статус из запроса или используем значения по умолчанию
    status_param = request.query_params.get('status')
    if status_param:
        records = Record.objects.filter(patient=patient, status=status_param).order_by('status')
    else:
        records = Record.objects.filter(patient=patient, status__in=[1, 2]).order_by('status')

    serializer = SimpleRecordSerializer(records, many=True)
    return Response(serializer.data)


# GET - список всех записей врача со статусом 'Подтверждено'
@swagger_auto_schema(
    tags=["GET-запросы"], 
    method='get', 
    operation_summary="Получение списка всех записей врача со статусом 'Подтверждено' (status=2)",
    responses={
        200: SimpleRecordSerializer(many=True),
        400: "Bad Request - Пользователь не является врачом.",
        403: "Forbidden - Сессия не найдена.",
        404: "Not Found - Пользователь не найден."
    })
@api_view(['GET'])
def get_records_by_doctor(request, format=None):
    if "session_id" in request.COOKIES:
        ssid = request.COOKIES["session_id"]
    else:
        return HttpResponseForbidden('Сессия не найдена')

    try:
        email = session_storage.get(ssid).decode('utf-8')
        user = User.objects.get(email=email)
    except (User.DoesNotExist, AttributeError):
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_doctor:
        return Response({"error": "Пользователь не врач."}, status=status.HTTP_400_BAD_REQUEST)

    doctor = Doctor.objects.get(user=user)

    # Получаем все записи, связанные с этим врачом, со статусом "Подтверждено"
    records = Record.objects.filter(doctor=doctor, status=2)

    serializer = SimpleRecordSerializer(records, many=True)
    return Response(serializer.data)


# GET - список всех лечений пациента с сортировкой по статусу по возрастанию
@swagger_auto_schema(
    tags=["GET-запросы"], 
    method='get', 
    operation_summary="Получение списка всех лечений пациента с сортировкой по статусу по возрастанию",
    responses={
        200: SimpleTreatmentSerializer(many=True),
        400: "Bad Request - Пользователь не является пациентом.",
        403: "Forbidden - Сессия не найдена.",
        404: "Not Found - Пользователь не найден."})
@api_view(['GET'])
def get_treatments_by_patient(request, format=None):
    if "session_id" in request.COOKIES:
        ssid = request.COOKIES["session_id"]
    else:
        return HttpResponseForbidden('Сессия не найдена')

    try:
        email = session_storage.get(ssid).decode('utf-8')
        user = User.objects.get(email=email)
    except (User.DoesNotExist, AttributeError):
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_patient:
        return Response({"error": "Пользователь не пациент."}, status=status.HTTP_400_BAD_REQUEST)

    patient = Patient.objects.get(user=user)
    treatments = Treatment.objects.filter(patient=patient).order_by('status')

    serializer = TreatmentSerializer(treatments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# GET - список всех лечений врача со статусом 'В процессе' (status=1)
@swagger_auto_schema(
    tags=["GET-запросы"],
    method='get',
    operation_summary="Получение списка всех лечений врача со статусом 'В процессе' (status=1)",
    responses={
        200: SimpleTreatmentSerializer(many=True),
        400: "Bad Request - Пользователь не является врачом.",
        403: "Forbidden - Сессия не найдена.",
        404: "Not Found - Пользователь не найден."})
@api_view(['GET'])
def get_treatments_by_doctor(request, format=None):
    if "session_id" in request.COOKIES:
        ssid = request.COOKIES["session_id"]
    else:
        return HttpResponseForbidden('Сессия не найдена')

    try:
        email = session_storage.get(ssid).decode('utf-8')
        user = User.objects.get(email=email)
    except (User.DoesNotExist, AttributeError):
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_doctor:
        return Response({"error": "Пользователь не врач."}, status=status.HTTP_400_BAD_REQUEST)

    doctor = Doctor.objects.get(user=user)
    treatments = Treatment.objects.filter(doctor=doctor, status=1)  # 1 соответствует статусу "В процессе"

    serializer = TreatmentSerializer(treatments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



# GET - список медикаментов пациента
@swagger_auto_schema(
    tags=["GET-запросы"], 
    method='get', 
    operation_summary="Получение списка медикаментов пациента",
    responses={
        200: MedicamentSerializer(many=True),
        400: 'Bad Request - Пользователь не пациент',
        403: 'Forbidden - Сессия не найдена',
        404: 'Not Found - Пациент не найден',
})
@api_view(['GET'])
def get_medicaments_by_patient(request, format=None):
    if "session_id" in request.COOKIES:
        ssid = request.COOKIES["session_id"]
    else:
        return HttpResponseForbidden('Сессия не найдена')

    try:
        email = session_storage.get(ssid).decode('utf-8')
        user = User.objects.get(email=email)
    except (User.DoesNotExist, AttributeError):
        return Response({"error": "Пациент не найден."}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_patient:
        return Response({"error": "Пользователь не пациент."}, status=status.HTTP_400_BAD_REQUEST)

    patient = Patient.objects.get(user=user)

    try:
        treatment = Treatment.objects.get(patient=patient)
    except Treatment.DoesNotExist:
        return Response({"error": "Лечение не найдено или не принадлежит данному пациенту."}, status=status.HTTP_404_NOT_FOUND)

    # Получаем все медикаменты, связанные с этим лечением
    treatment_medicaments = TreatmentMedicament.objects.filter(treatment=treatment)
    medicaments = [tm.medicament for tm in treatment_medicaments]

    serializer = MedicamentSerializer(medicaments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# GET - список рентген снимов пациента
@swagger_auto_schema(tags=["GET-запросы"], method='get', operation_summary="Получение снимков пациента",
    responses={
        200: SnapshotSerializer(many=True),
        400: 'Bad Request',
        403: 'Forbidden',
        404: 'Not Found',
})
@api_view(['GET'])
@permission_classes([AllowAny])
def get_patient_snapshots(request):
    if "session_id" in request.COOKIES:
        ssid = request.COOKIES["session_id"]
    else:
        return HttpResponseForbidden('Сессия не найдена')

    try:
        email = session_storage.get(ssid).decode('utf-8')
        user = User.objects.get(email=email)
    except (User.DoesNotExist, AttributeError):
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_patient:
        return Response({"error": "Пользователь не пациент."}, status=status.HTTP_400_BAD_REQUEST)

    patient = Patient.objects.get(user=user)
    snapshots = Snapshot.objects.filter(record__patient=patient, type=2)  # 2 - это тип "Рентген"
    serializer = SnapshotSerializer(snapshots, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


#########################################################################################################
# ------------------------------------------------- PUT -------------------------------------------------
#########################################################################################################


# PUT - изменение врачом статуса записи на "Завершено"
@swagger_auto_schema(tags=["PUT-запросы"], method='put', operation_summary="Изменение врачом статуса записи на 'Завершено'")
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_record_by_doctor(request, record_id):
    try:
        record = Record.objects.get(pk=record_id)
    except Record.DoesNotExist:
        return Response("Запись не найдена.", status=status.HTTP_404_NOT_FOUND)
    
    if record.status == 2:
        record.status = 4  # 4 - это статус "Завершено"
    elif record.status == 1:
        return Response("Запись не подтверждена администратором, ее нельзя завершить.", status=status.HTTP_400_BAD_REQUEST)
    elif record.status == 3:
        return Response("Запись отменена, ее нельзя завершить.", status=status.HTTP_400_BAD_REQUEST)
    elif record.status == 4:
        return Response("Запись уже завершена", status=status.HTTP_400_BAD_REQUEST)

    if record.start_time:
        record.end_time = datetime.now()
    else:
        return Response("Время начала записи не указано.", status=status.HTTP_400_BAD_REQUEST)

    record.save()

    serializer = RecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)


# PUT - изменение админом статуса записи на "Подтверждено"
@swagger_auto_schema(
    tags=["PUT-запросы"], 
    method='put', 
    operation_summary="Изменение админом статуса записи на 'Подтверждено'")
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_record_by_admin(request, record_id):
    try:
        record = Record.objects.get(pk=record_id)
    except Record.DoesNotExist:
        return Response("Запись не найдена.", status=status.HTTP_404_NOT_FOUND)

    if record.status == 1:
        record.status = 2  # 2 - это статус "Подтверждено"
    else:
        return Response("Запись нельзя подтвердить, неверный статус записи.", status=status.HTTP_400_BAD_REQUEST)

    record.save()

    serializer = RecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)


# PUT - изменение пациентом статуса записи на "Отменено" (отмена записи)
@swagger_auto_schema(tags=["PUT-запросы"], method='put', operation_summary="Изменение пациентом статуса записи на 'Отменено' (отмена записи)")
@api_view(['PUT'])
@permission_classes([AllowAny])
def cancel_record_by_patient(request, record_id):
    try:
        record = Record.objects.get(pk=record_id)
    except Record.DoesNotExist:
        return Response({"error": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)

    if record.status == 4:
        return Response({"error": "Запись уже завершена. Запись нельзя отменить"}, status=status.HTTP_400_BAD_REQUEST)

    if record.status == 3:
        return Response({"error": "Запись уже отменена. Запись нельзя отменить повторно"}, status=status.HTTP_400_BAD_REQUEST)

    # Проверяем, что запись принадлежит текущему пациенту
    if record.patient.user != request.user:
        return Response({"error": "У вас нет прав для отмены этой записи."}, status=status.HTTP_403_FORBIDDEN)

    # Обновляем статус записи на "Отменено"
    record.status = 3  # 3 - это статус "Отменено"
    record.save()

    return Response({"status": "Запись успешно отменена."}, status=status.HTTP_200_OK)


@swagger_auto_schema(tags=["PUT-запросы"], method='put', operation_summary="Изменение врачом статуса лечения на 'Завершено'")
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_treatment_by_doctor(request, treatment_id):
    try:
        treatment = Treatment.objects.get(pk=treatment_id)
    except Record.DoesNotExist:
        return Response("Лечение не найдено.", status=status.HTTP_404_NOT_FOUND)

    if treatment.status == 1:
        treatment.status = 2  # 2 - это статус "Завершено"
        treatment.date_completion = datetime.now()
    else:
        return Response("Лечение нельзя завершить, неверный статус лечения.", status=status.HTTP_400_BAD_REQUEST)

    treatment.save()

    serializer = RecordSerializer(treatment)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    tags=["PUT-запросы"],
    method='put',
    operation_summary="Перенос записи на другое время",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['start_time'],
        properties={
            'start_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Новое время начала записи'),
        },
    ),
    responses={
        200: "Запись успешно перенесена",
        400: "Неверный формат времени или отсутствует обязательное поле",
        404: "Запись не найдена",
        403: "Запись уже завершена и не может быть изменена",
    }
)
@api_view(['PUT'])
@permission_classes([AllowAny])
def reschedule_record(request, record_id):
    # Получаем данные из запроса
    start_time = request.data.get('start_time')

    if not start_time:
        return Response({"error": "Необходимо указать новое время начала записи."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Преобразуем строку времени в объект datetime
        new_start_time = datetime.fromisoformat(start_time)
    except ValueError:
        return Response({"error": "Неверный формат времени. Используйте формат ISO 8601."}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем объект записи
    record = get_object_or_404(Record, pk=record_id)

    # Проверяем, что запись не завершена
    if record.status == 4:  # 4 - это статус "Завершено"
        return Response({"error": "Запись уже завершена и не может быть изменена."}, status=status.HTTP_403_FORBIDDEN)

    # Изменяем время начала записи
    record.start_time = new_start_time
    record.save()

    serializer = RecordSerializer(record)
    return Response(serializer.data, status=status.HTTP_200_OK)


##########################################################################################################
# ------------------------------------------------- POST -------------------------------------------------
##########################################################################################################


# Регистрация пользователя (админ, пациент)
@swagger_auto_schema(tags=["POST-запросы"], method='post', request_body=UserSerializer, operation_summary="Регистрация пациента и администратора")
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    if User.objects.filter(email=request.data['email']).exists():
        return Response({'status': 'Exist'}, status=400)
    user_data = {
        'email': request.data['email'],
        'phone_number': request.data['phone_number'],
        'password': request.data['password'],
        'is_admin': request.data['is_admin'],
        'is_doctor': request.data['is_doctor'],
        'is_patient': request.data['is_patient']
    }
    print(user_data)
    serializer = UserSerializer(data=user_data)
    if serializer.is_valid():
        print(serializer.data)
        user_key = User.objects.create_user(email=serializer.data['email'],
                                        phone_number=serializer.data['phone_number'],
                                        password=serializer.data['password'],
                                        is_admin=serializer.data['is_admin'],
                                        is_doctor=serializer.data['is_doctor'],
                                        is_patient=serializer.data['is_patient'])
        print(request.data['is_patient'])
        if request.data['is_patient']:
            Patient.objects.create(user=user_key, 
                                   name=request.data['name'], 
                                   surname=request.data['surname'],
                                   patronymic=request.data['patronymic'],
                                   birth_date=request.data['birth_date'])
            user_data['name'] = request.data['name']
            user_data['surname'] = request.data['surname']
            user_data['patronymic'] = request.data['patronymic']
            user_data['birth_date'] = request.data['birth_date']
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, serializer.data['email'])
        response = Response(user_data, status=status.HTTP_201_CREATED)
        response.set_cookie("session_id", random_key)
        return response
    return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Регистрация пользователя (врач)
@swagger_auto_schema(tags=["POST-запросы"], method='post', request_body=DoctorSerializer, operation_summary="Создание доктора администратором")
@api_view(['POST'])
@permission_classes([AllowAny])
def create_doctor(request):
    if User.objects.filter(email=request.data['email']).exists():
        return Response({'status': 'Exist'}, status=400)
    user_data = {
        'email': request.data['email'],
        'phone_number': request.data['phone_number'],
        'password': request.data['password'],
        'is_admin': request.data['is_admin'],
        'is_doctor': request.data['is_doctor'],
        'is_patient': request.data['is_patient'],
    }
    print(user_data)
    serializer = UserSerializer(data=user_data)
    if serializer.is_valid():
        print(serializer.data)
        user_key = User.objects.create_user(email=serializer.data['email'],
                                            phone_number=serializer.data['phone_number'],
                                            password=serializer.data['password'],
                                            is_admin=serializer.data['is_admin'],
                                            is_doctor=serializer.data['is_doctor'],
                                            is_patient=serializer.data['is_patient'])
        print(request.data['is_doctor'])
        if request.data['is_doctor']:
            specialization_name = request.data['specialization']
            specialization, created = Specialization.objects.get_or_create(name=specialization_name)

            Doctor.objects.create(user=user_key,
                                    specialization=specialization,
                                    name=request.data['name'], 
                                    surname=request.data['surname'],
                                    patronymic=request.data['patronymic'],
                                    image_path=request.data['image_path'])
            user_data['specialization'] = specialization.name
            user_data['name'] = request.data['name']
            user_data['surname'] = request.data['surname']
            user_data['patronymic'] = request.data['patronymic']
            user_data['image_path'] = request.data['image_path']
        #random_key = str(uuid.uuid4())
        #session_storage.set(random_key, serializer.data['email'])
        response = Response(user_data, status=status.HTTP_201_CREATED)
        #response.set_cookie("session_id", random_key)
        return response
    return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# Вход в профиль
@swagger_auto_schema(
    tags=["POST-запросы"],
    method='post',
    request_body=LoginSerializer,
    operation_summary="Вход в профиль",
    responses={
        201: LoginSuccessResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():  # Проверка валидности данных
        username = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, email=username, password=password)
        if user is not None:
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, username)
            user_data = {
                "id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
                "is_superuser": user.is_superuser,
                "is_admin": user.is_admin,
                "is_doctor": user.is_doctor,
                "is_patient": user.is_patient
            }
            response = Response(user_data, status=status.HTTP_201_CREATED)
            response.set_cookie("session_id", random_key)
            return response
        else:
            return Response({'status': 'error', 'error': 'login failed'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'status': 'error', 'error': 'invalid input'}, status=status.HTTP_400_BAD_REQUEST)


# Выход из профиля
@swagger_auto_schema(tags=["POST-запросы"], method='post', operation_summary="Выход из профиля")
@api_view(['POST'])
@permission_classes([IsAuth])
def logout(request):
    ssid = request.COOKIES["session_id"]
    print(ssid)
    if session_storage.exists(ssid):
        session_storage.delete(ssid)
        response_data = {'status': 'Success'}
    else:
        response_data = {'status': 'Error', 'message': 'Session does not exist'}
    return Response(response_data)


@swagger_auto_schema(tags=["POST-запросы"], method='post', operation_summary="Обновление рейтинга врача",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['rating', 'patient_id', 'doctor_id'],
        properties={
            'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Новый рейтинг врача (от 1 до 5)'),
            'doctor_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID врача'),
        },
    ),
    responses={
        201: "Рейтинг врача успешно обновлен",
        400: "Ошибка в запросе",
        404: "Врач или пациент не найдены",
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def update_doctor_rating(request, doctor_id):
    new_rating = request.data.get('rating')
    doctor_id = request.data.get('doctor_id')

    if not new_rating or not doctor_id:
        return Response({"error": "Missing rating or doctor_id."}, status=status.HTTP_400_BAD_REQUEST)

    if "session_id" in request.COOKIES:
        ssid = request.COOKIES["session_id"]
    else:
        return HttpResponseForbidden('Сессия не найдена')
    
    try:
        email = session_storage.get(ssid).decode('utf-8')
        user = User.objects.get(email=email)
    except (User.DoesNotExist, AttributeError):
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    if not user.is_patient:
        return Response({"error": "Пользователь не пациент."}, status=status.HTTP_400_BAD_REQUEST)

    patient = Patient.objects.get(user=user)

    try:
        doctor = Doctor.objects.get(pk=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

    if 1 <= new_rating <= 5:
        # Создаем новую оценку
        Rating.objects.create(doctor=doctor, patient=patient, score=new_rating)

        # Пересчитываем средний рейтинг врача
        average_rating = Rating.objects.filter(doctor=doctor).aggregate(Avg('score'))['score__avg']
        doctor.rating = round(average_rating) if average_rating is not None else 0
        doctor.save()

        return Response({"rating": doctor.rating}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Rating must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)


# POST - создание новой записи пациентом
@swagger_auto_schema(
    tags=["POST-запросы"],
    method='post',
    operation_summary="Создание новой записи пациентом",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['doctor_id', 'procedure_id', 'start_time'],
        properties={
            'treatment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID лечения'),
            'doctor_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID доктора'),
            'procedure_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID процедуры'),
            'start_time': openapi.Schema(type=openapi.TYPE_INTEGER, description='Время начала'),
        },
    ),
    responses={
        201: "Запись успешно создана",
        400: "Необходимо передать либо treatment_id, либо doctor_id или необходимые данные отсутствуют",
        404: "Данные не найдены",
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_record(request, format=None):
    # Получаем данные из запроса
    treatment_id = request.data.get('treatment_id')
    doctor_id = request.data.get('doctor_id')
    procedure_id = request.data.get('procedure_id')
    start_time = request.data.get('start_time')

    if not treatment_id and not doctor_id:
        return Response("Необходимо передать либо treatment_id, либо doctor_id.", status=status.HTTP_400_BAD_REQUEST)

    if not procedure_id or not start_time:
        return Response("Необходимые данные отсутствуют.", status=status.HTTP_400_BAD_REQUEST)

    # Получаем session_id из cookie
    session_id = request.COOKIES.get('session_id')
    if not session_id:
        return Response("Отсутствует session_id в cookie.", status=status.HTTP_400_BAD_REQUEST)

    # Получаем email пользователя из session_storage
    user_email = session_storage.get(session_id)
    if not user_email:
        return Response("Не удалось определить пользователя по session_id.", status=status.HTTP_400_BAD_REQUEST)

    # Получаем объект пользователя
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return Response("Пользователь не найден.", status=status.HTTP_404_NOT_FOUND)

    # Получаем объект пациента
    try:
        patient = Patient.objects.get(user=user)
    except Patient.DoesNotExist:
        return Response("Пациент не найден.", status=status.HTTP_404_NOT_FOUND)

    try:
        # Получаем объект процедуры
        procedure = Procedure.objects.get(pk=procedure_id)

        if treatment_id:
            # Получаем объект лечения и доктора из него
            treatment = Treatment.objects.get(pk=treatment_id)
            doctor = treatment.doctor
        elif doctor_id:
            # Получаем объект доктора
            doctor = Doctor.objects.get(pk=doctor_id)
            treatment = None

        # Создаем новую запись
        record = Record.objects.create(
            procedure=procedure,
            doctor=doctor,
            patient=patient,
            treatment=treatment,
            status=1,  # Статус "Ожидание подтверждения"
            start_time=start_time,
            end_time=None  # Время окончания оставляем пустым
        )

        serializer = RecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Treatment.DoesNotExist:
        return Response("Лечение не найдено.", status=status.HTTP_404_NOT_FOUND)
    except Procedure.DoesNotExist:
        return Response("Процедура не найдена.", status=status.HTTP_404_NOT_FOUND)
    except Doctor.DoesNotExist:
        return Response("Доктор не найден.", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(f"Ошибка при создании записи: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# POST - создание нового лечения доктором
@swagger_auto_schema(
    tags=["POST-запросы"],
    method='post',
    operation_summary="Создание нового лечения с диагнозом",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['patient_id', 'diagnose_name', 'diagnose_description', 'description'],
        properties={
            'patient_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID пациента'),
            'diagnose_name': openapi.Schema(type=openapi.TYPE_STRING, description='Название диагноза'),
            'diagnose_description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание диагноза'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Описание лечения')
        },
    ),
    responses={
        201: "Лечение успешно создано",
        400: "Необходимые данные отсутствуют в запросе",
        404: "Данные не найдены",
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_treatment(request, format=None):
    serializer = TreatmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Получаем данные из запроса
    patient_id = serializer.validated_data.get('patient_id')
    diagnose_name = serializer.validated_data.get('diagnose_name')
    diagnose_description = serializer.validated_data.get('diagnose_description')
    description = serializer.validated_data.get('description')

    if not patient_id or not diagnose_name or not diagnose_description or not description:
        return Response("Необходимые данные отсутствуют.", status=status.HTTP_400_BAD_REQUEST)

    # Получаем session_id из cookie
    session_id = request.COOKIES.get('session_id')
    if not session_id:
        return Response("Отсутствует session_id в cookie.", status=status.HTTP_400_BAD_REQUEST)

    # Получаем email пользователя из session_storage
    user_email = session_storage.get(session_id)
    if not user_email:
        return Response("Не удалось определить пользователя по session_id.", status=status.HTTP_400_BAD_REQUEST)

    # Получаем объект пользователя
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return Response("Пользователь не найден.", status=status.HTTP_404_NOT_FOUND)

    # Получаем объект доктора
    try:
        doctor = Doctor.objects.get(user=user)
    except Doctor.DoesNotExist:
        return Response("Доктор не найден.", status=status.HTTP_404_NOT_FOUND)

    try:
        # Получаем объект пациента
        patient = Patient.objects.get(pk=patient_id)

        # Создаем новый диагноз
        diagnose = Diagnose.objects.create(
            name=diagnose_name,
            decription=diagnose_description
        )

        # Создаем новое лечение со статусом 1 ("В процессе") и текущей датой и временем
        treatment = Treatment.objects.create(
            doctor=doctor,
            patient=patient,
            diagnose=diagnose,
            status=1,  # Устанавливаем статус "В процессе"
            date_creation=datetime.now(),  # Устанавливаем текущую дату и время
            description=description
        )

        return Response({"message": "Лечение успешно создано"}, status=status.HTTP_201_CREATED)
    except Patient.DoesNotExist:
        return Response("Пациент не найден.", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(f"Ошибка при создании лечения: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)