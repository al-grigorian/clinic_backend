from django.db import models

# Create your models here.

# Пациенты
class Patient(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    birth_date = models.DateField()
    telephone = models.CharField(max_length=15)
    password = models.CharField(max_length=500)

    class Meta: 
        verbose_name_plural = "Patients" 
        managed = True

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"

class Specialization(models.Model):
    name = models.CharField(max_length=100)

    class Meta: 
        verbose_name_plural = "Specializations" 
        managed = True
        
    def __str__(self):
        return self.name

# Врачи
class Doctor(models.Model):
    specialization = models.ForeignKey(Specialization, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    image_path = models.TextField()
    rating = models.IntegerField()
    telephone = models.CharField(max_length=15)
    password = models.CharField(max_length=500)

    class Meta: 
        verbose_name_plural = "Doctors" 
        managed = True

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"

# Диагнозы
class Diagnose(models.Model):
    name = models.CharField(max_length=100)
    decription = models.TextField()

    class Meta: 
        verbose_name_plural = "Diagnosises" 
        managed = True

    def __str__(self):
        return self.name

# Процедуры
class Procedure(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.BigIntegerField()

# Лечение
class Treatment(models.Model):
    STATUS_TREATMENT = ( 
        (1, 'В процессе'),
        (2, 'Завершено'),
    )

    status = models.IntegerField(choices=STATUS_TREATMENT)
    date_appointment = models.DateTimeField()
    description = models.TextField()

# Лекарства
class Medicament(models.Model):
    name = models.CharField(max_length=100)
    producer_country = models.CharField(max_length=100)
    purpose = models.TextField()
    contraindications = models.TextField()
    production_date = models.DateField()
    
    class Meta: 
        verbose_name_plural = "Medicaments" 
        managed = True

    def __str__(self):
        return self.name


class TreatmentMedicament(models.Model):
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)

    class Meta: 
        verbose_name_plural = "Treatments with medicaments" 
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
        (3, 'В процессе'),
        (4, 'Отменено'),
        (5, 'Перенесено'),
        (6, 'Завершено'),
    )

    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    diagnose = models.ForeignKey(Diagnose, null=True, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    treatment = models.ForeignKey(Treatment, null=True, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUS_CHOICES)
    duration = models.DecimalField(max_digits=4, decimal_places=2)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

# Доктора и проводимые ими процедуры
class DoctorsProcedures(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)

    class Meta: 
        verbose_name_plural = "Doctors with Procedures" 
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


# Счета для оплаты
class Account(models.Model):
    amount = models.BigIntegerField()
    treatment = models.OneToOneField(Treatment, on_delete=models.CASCADE)