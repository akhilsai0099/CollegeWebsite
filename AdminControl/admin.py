from django.contrib import admin, messages
from .models import UserData, Department
from django import forms
from django.urls import path, reverse
from django.shortcuts import render
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
            csv_file = request.FILES['csv_upload']

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, "Please upload a csv file")
                return HttpResponseRedirect(request.path_info)

            decoded_file = csv_file.read().decode('utf-8').splitlines()

            reader = csv.reader(decoded_file)

            for row in reader:
                print(row)

                userdata = UserData.objects.update_or_create(rollno=row[0],
                                                             name=row[1],
                                                             branch=row[2],
                                                             email=row[3],
                                                             phone=row[4],
                                                             scgpa=row[7],
                                                             total_credits=row[5],
                                                             total_grade=row[6])
                # userdata.save()
            messages.success(
                request, "Data has been uploaded from the CSV file")
            return HttpResponseRedirect(request.path_info)

        form = CsvImportForm()
        body = {"form": form}
        return render(request, 'admin/upload-csv.html', body)


admin.site.register(UserData, UserDataControl)
