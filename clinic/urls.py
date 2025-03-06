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
    path('patients/', views.get_patients, name='patients-list'), # Получение списка всех пациентов
    path('procedures/', views.get_procedures, name='procedures-list'), # Получение списка всех процедур
    path('specializations/', views.get_specializations, name='specializations-list'), # Получение списка всех специализаций
    path('doctors/by-procedure/<int:procedure_id>/', views.get_doctors_by_procedure, name='get_doctors_by_procedure'), # Получение списка врачей, выполняющих конкретную выбранную процедуру
    path('records/by-patient/<int:patient_id>/', views.get_records_by_patient, name='get_records_by_patient'), # Получение списка записей конкретного пациента
    path('records_by_doctor/<int:doctor_id>/', views.get_records_by_doctor, name='get_records_by_doctor'), # Получение списка записей конкретного врача
    path('treatments_by_patient/<int:patient_id>/', views.get_treatments_by_patient, name='get_treatments_by_patient'), # Получение списка лечений конкретного пациента
    path('medicaments/by-treatment/<int:treatment_id>/', views.get_medicaments_by_treatment, name='get_medicaments_by_treatment'),  # Получение списка медикаментов, относящихся к конкретному лечению
    
    # PUT
    path('records/update-by-doctor/<int:record_id>/', views.update_record_by_doctor, name='update_record_by_doctor'),  # Изменение статуса записи врачом на "Завершено"
    path('records/update-by-admin/<int:record_id>/', views.update_record_by_admin, name='update_record_by_admin'),  # Обновление статуса заявки админом на "Подтверждено"

    # POST

    # DELETE
    
    
]
