from django.db import models
from django.contrib.auth.models import UserManager,User, PermissionsMixin, AbstractBaseUser
from django.conf import settings
# Create your models here.

# Пациенты
class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    birth_date = models.DateField()

    class Meta:
        db_table = 'patients'
        verbose_name_plural = "Пациенты" 
        managed = True

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"

class Specialization(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'specializations'
        verbose_name_plural = "Специализации" 
        managed = True
        
    def __str__(self):
        return self.name

# Врачи
class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    specialization = models.ForeignKey(Specialization, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    image_path = models.TextField()
    rating = models.IntegerField(default=0)

    class Meta:
        db_table = 'doctors'
        verbose_name_plural = "Врачи" 
        managed = True

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"

# Диагнозы
class Diagnose(models.Model):
    name = models.CharField(max_length=100)
    decription = models.TextField()

    class Meta:
        db_table = 'diagnoses'
        verbose_name_plural = "Диагнозы" 
        managed = True

    def __str__(self):
        return self.name

# Процедуры
class Procedure(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.BigIntegerField()

    class Meta:
        db_table = 'procedures'
        verbose_name_plural = "Процедуры" 
        managed = True

    def __str__(self):
        return self.name

# Лечение
class Treatment(models.Model):
    STATUS_TREATMENT = ( 
        (1, 'В процессе'),
        (2, 'Завершено'),
    )

    doctor = models.ForeignKey(Doctor, blank=True, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, blank=True, null=True, on_delete=models.CASCADE)
    diagnose = models.ForeignKey(Diagnose, blank=True, null=True,  on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_TREATMENT)
    date_creation = models.DateTimeField()
    date_completion = models.DateTimeField(null=True)
    description = models.TextField()

    class Meta:
        db_table = 'treatments'
        verbose_name_plural = "Лечения" 
        managed = True

    def __str__(self):
        return self.name

# Лекарства
class Medicament(models.Model):
    name = models.CharField(max_length=100)
    producer_country = models.CharField(max_length=100)
    purpose = models.TextField()
    contraindications = models.TextField()
    production_date = models.DateField()
    
    class Meta:
        db_table = 'medicaments'
        verbose_name_plural = "Медикаменты" 
        managed = True

    def __str__(self):
        return self.name


class TreatmentMedicament(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)

    class Meta:
        db_table = 'treatmentmedicament'
        verbose_name_plural = "Лечения и их медикаменты" 
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['treatment', 'medicament'], name='unique_medicaments_treatment')
        ]

    def __str__(self):
        return f"{self.treatment}-{self.medicament}"

# Записи
class Record(models.Model):
    STATUS_CHOICES = ( 
        (1, 'Ожидание подтверждения'),
        (2, 'Подтверждено'),
        (3, 'Отменено'),
        (4, 'Завершено')
    )

    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    treatment = models.ForeignKey(Treatment, null=True, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUS_CHOICES)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    class Meta:
        db_table = 'records'
        verbose_name_plural = "Записи" 
        managed = True

# Врачи и проводимые ими процедуры
class DoctorsProcedures(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)

    class Meta:
        db_table = 'doctorprocedure'
        verbose_name_plural = "Врачи и процедуры" 
        managed = True
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'procedure'], name='unique_doctor_procedure')
        ]

    def __str__(self):
        return f"{self.doctor}-{self.procedure}"

# Снимки
class Snapshot(models.Model):
    SNAPSHOT_TYPE = (
        (1, "3D модель"),
        (2, "Рентген"),
    )

    path = models.TextField()
    type = models.IntegerField(choices=SNAPSHOT_TYPE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)

    class Meta:
        db_table = 'snapshots'
        verbose_name_plural = "Снимки" 
        managed = True

    def __str__(self):
        return f"{self.doctor}-{self}"

# Счета для оплаты
class Account(models.Model):
    amount = models.BigIntegerField()
    treatment = models.OneToOneField(Treatment, on_delete=models.CASCADE)

    class Meta:
        db_table = 'accounts'
        verbose_name_plural = "Счета" 
        managed = True

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    phone_number = models.CharField(unique=True, max_length=15, verbose_name="Телефон")
    password = models.CharField(max_length=150, verbose_name="Пароль")    
    is_admin = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    is_doctor = models.BooleanField(default=False, verbose_name="Является ли пользователь врачом?")
    is_patient = models.BooleanField(default=False, verbose_name="Является ли пользователь пациентом?")

    USERNAME_FIELD = 'email'

    objects =  NewUserManager()

    class Meta:
        db_table = 'users'
        verbose_name_plural = "Пользователи" 
        managed = True

class Rating(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='ratings')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        db_table = 'ratings'
        unique_together = ('doctor', 'patient')  # Один пациент может оставить только одну оценку для одного врача
        managed = True
        verbose_name_plural = "Рейтинги"