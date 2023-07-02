from django.contrib import admin, messages
from .models import UserData
from django import forms
from django.urls import path, reverse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
import csv

# Register your models here.


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()
    csv_upload.label = "Upload a CSV file"


class UserDataControl(admin.ModelAdmin):
    list_display = ("rollno", "name", "branch", "scgpa")

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('upload-csv/', self.upload_csv)]
        return my_urls+urls

    def upload_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_upload')

            if not csv_file:
                messages.warning(request, "Please upload a CSV file")
                return HttpResponseRedirect(request.path_info)

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, "Please upload a CSV file")
                return HttpResponseRedirect(request.path_info)

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)

            for row in reader:
                rollno = row[0]
                name = row[1]
                branch = row[2]
                email = row[3]
                phone = row[4]
                scgpa = row[7]
                total_credits = row[5]
                total_grade = row[6]

                try:
                    userdata, created = UserData.objects.update_or_create(
                        rollno=rollno,
                        defaults={
                            'name': name,
                            'branch': branch,
                            'email': email,
                            'phone': phone,
                            'scgpa': scgpa,
                            'total_credits': total_credits,
                            'total_grade': total_grade
                        }
                    )

                    if created:
                        User.objects.create_user(
                            username=rollno,
                            password=phone,
                            first_name=name
                        )
                        messages.success(
                            request, f"Data added for Roll No: {rollno}")
                    else:
                        messages.success(
                            request, f"Data updated for Roll No: {rollno}")
                except Exception as e:
                    messages.error(
                        request, f"Error updating/adding data for Roll No: {rollno} - {str(e)}")

            messages.success(
                request, "Data has been uploaded from the CSV file")
            return HttpResponseRedirect(request.path_info)

        form = CsvImportForm()
        body = {"form": form}
        return render(request, 'admin/upload-csv.html', body)


admin.site.register(UserData, UserDataControl)
