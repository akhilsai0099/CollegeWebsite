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

    def __str__(self):
        return self.name

    class Meta:  # new
        verbose_name_plural = "Semester Data"


class Department(models.Model):
    dept_id = models.CharField(primary_key=True, max_length=5)
    dept_name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
