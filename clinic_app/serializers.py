from .models import *
from rest_framework import serializers

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Doctor
        # Поля, которые мы сериализуем
        fields = "__all__"
    
class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = "__all__"

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = "__all__"

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = "__all__"

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = "__all__"

class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = "__all__"

class MedicamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicament
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):    
    is_admin = serializers.BooleanField(default=False, required=False)
    is_doctor = serializers.BooleanField(default=False, required=False)
    is_patient = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'is_admin', 'is_doctor', 'is_patient']
        
