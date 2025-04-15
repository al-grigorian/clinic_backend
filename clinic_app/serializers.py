from .models import *
from rest_framework import serializers
from .models import Record, Patient, Doctor, Procedure


class LoginSuccessResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    is_superuser = serializers.BooleanField()
    is_admin = serializers.BooleanField()
    is_doctor = serializers.BooleanField()
    is_patient = serializers.BooleanField()


class LoginSuccessResponseSerializer2(serializers.Serializer):
    message = serializers.CharField()
    token = serializers.CharField()


class SimpleTreatmentSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    diagnose = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = '__all__'  # ['id', 'doctor', 'patient', 'diagnose', 'status', 'date_creation', 'date_completion', 'description']

    def get_doctor(self, obj):
        return f"{obj.doctor.surname} {obj.doctor.name} {obj.doctor.patronymic}"

    def get_patient(self, obj):
        return f"{obj.patient.surname} {obj.patient.name} {obj.patient.patronymic}"

    def get_diagnose(self, obj):
        return obj.diagnose.name if obj.diagnose else None
    

class SimpleRecordSerializer(serializers.ModelSerializer):
    procedure = serializers.CharField(source='procedure.name')
    doctor = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

    class Meta:
        model = Record
        fields = '__all__'#['id', 'procedure', 'doctor', 'patient', 'treatment', 'status', 'start_time', 'end_time']

    def get_doctor(self, obj):
        return f"{obj.doctor.surname} {obj.doctor.name} {obj.doctor.patronymic}"

    def get_patient(self, obj):
        return f"{obj.patient.surname} {obj.patient.name} {obj.patient.patronymic}"

class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = "__all__"

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
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
        fields = ['id', 'email', 'phone_number', 'password', 'is_admin', 'is_doctor', 'is_patient']


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshot
        fields = '__all__'

class RecordSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    procedure = ProcedureSerializer(read_only=True)
    
    class Meta:
        model = Record
        fields = ['id', 'patient', 'doctor', 'procedure', 'treatment', 'status', 'start_time', 'end_time']