from django.db import models

# Create your models here.


class UserData(models.Model):
    rollno = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=30)
    branch = models.CharField(max_length=5)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    total_credits = models.DecimalField(max_digits=5, decimal_places=2)
    total_grade = models.CharField(max_length=1)
    scgpa = models.DecimalField(max_digits=3, decimal_places=2)
    batchCode = models.CharField(max_length=4, null=False)
    honorsDept = models.CharField(max_length=5, null=True)
    minorsDept = models.CharField(max_length=5, null=True)

    def __str__(self):
        return self.name

    class Meta:  # new
        verbose_name_plural = "Semester Data"


class HonorsModel(models.Model):
    rollno = models.CharField(primary_key=True, max_length=10)
    dept = models.CharField(max_length=5)
    scgpa = models.DecimalField(max_digits=3, decimal_places=2)
    selectedDept = models.CharField(max_length=5)

    def __str__(self):
        return self.rollno

    class Meta:  # new
        verbose_name_plural = "Honors Applied Data"


class MinorsModel(models.Model):
    rollno = models.CharField(primary_key=True, max_length=10)
    courseChoice1 = models.CharField(max_length=5)
    courseChoice2 = models.CharField(max_length=5)
    scgpa = models.DecimalField(max_digits=3, decimal_places=2)
    selectedDept = models.CharField(max_length=5)

    def __str__(self):
        return self.rollno

    class Meta:  # new
        verbose_name_plural = "Minors Applied Data"
