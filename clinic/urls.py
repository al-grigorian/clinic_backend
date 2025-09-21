"""
URL configuration for clinic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from clinic_app import views
from rest_framework import permissions 
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="alx050@mail.ru"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # GET
    path('doctors/', views.get_doctors, name='doctors-list'), # Получение списка всех врачей
    path('procedures/', views.get_procedures, name='procedures-list'), # Получение списка всех процедур
    path('doctors/by-procedure/<int:procedure_id>/', views.get_doctors_by_procedure, name='get_doctors_by_procedure'), # Получение списка врачей, выполняющих конкретную выбранную процедуру
    path('doctors/<int:doctor_id>/available-slots/', views.get_available_slots, name='available-slots'),

    #path('specializations/', views.get_specializations, name='specializations-list'), # Получение списка всех специализаций
    #path('procedures/<int:procedure_id>/', views.get_procedure_by_id, name='get-procedure-by-id'), # Получение процедуры по ID
    #path('doctors/<int:doctor_id>/', views.get_doctor_by_id, name='get-doctor-by-id'), # Получение врача по ID
    #path('patients/', views.get_patients, name='patients-list'), # Получение списка всех пациентов

    path('records/by-admin/', views.get_pending_records, name='get_pending_records'), # Получение списка записей со статусом "Ожидание подтверждения"
    path('records/by-patient/', views.get_records_by_patient, name='get_records_by_patient'), # Получение списка всех записей пациента с фильтром по статусу. Если статус не передан в параметре, по умолчанию выведет список записей со статусом 'Ожидание подтверждения' и 'Подтверждено'
    path('records/by-doctor/', views.get_records_by_doctor, name='get_records_by_doctor'), # Получение списка всех записей врача со статусом "Подтверждено"
    path('treatments/by-patient/', views.get_treatments_by_patient, name='get_treatments_by_patient'), # Получение списка лечений пациента
    path('treatments/by-doctor/', views.get_treatments_by_doctor, name='get_treatments_by_doctor'), # Получение списка лечений врача со статусом 'В процессе'
    path('medicaments/by-patient/', views.get_medicaments_by_patient, name='get_medicaments_by_treatment'),  # Получение списка медикаментов пациента
    path('patients/snapshots/', views.get_patient_snapshots, name='get-patient-snapshots'), # Получение списка рентген снимов пациента
    path('patients/3d-snapshots/', views.get_patient_snapshots, name='get-patient-snapshots'),
    path('user_info', views.user_info, name='user_info'),

    # PUT
    path('records/update-by-doctor/<int:record_id>/', views.update_record_by_doctor, name='update_record_by_doctor'),  # Изменение статуса записи врачом на "Завершено"
    path('records/update-by-admin/<int:record_id>/', views.update_record_by_admin, name='update_record_by_admin'),  # Изменение статуса записи админом на "Подтверждено"
    path('records/cancel/<int:record_id>', views.cancel_record_by_patient, name='cancel-record'), # Изменение статуса записи пациентом на "Отменено"
    path('treatments/update-by-doctor/<int:treatment_id>', views.update_treatment_by_doctor, name='update_treatment_by_doctor'), # Изменение статуса лечения врачом на "Завершено"
    path('records/reschedule/<int:record_id>/', views.reschedule_record, name='reschedule-record'), # Перенос записи на другое время

    # POST
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/',  views.login, name='login'), # Авторизация
    path('logout/', views.logout, name='logout'), # Выход
    path('create_user/', views.create_user, name='create-user'), # Регистрация
    path('create_doctor/', views.create_doctor, name='create-doctor'), # Создание доктора
    path('doctors/rate/', views.update_doctor_rating, name='update-doctor-rating'),  # Добавление оценки доктору
    path('create_record/', views.create_record, name='create-record'), # Создание новой записи
    path('create_treatment/', views.create_treatment, name='create-treatment') # Создание нового лечения
]