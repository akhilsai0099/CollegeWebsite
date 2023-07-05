from django.contrib import admin, messages
from .models import UserData, HonorsModel, MinorsModel
from django import forms
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponseRedirect
from .views import upload_data_from_csv
import csv

# Register your models here.

FILTERNUMBER = 21


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()
    csv_upload.label = "Upload a CSV file"
    batchCode = forms.CharField()
    batchCode.label = "Enter the batchCode "


class UserDataControl(admin.ModelAdmin):
    list_display = (
        "batchCode",
        "rollno",
        "name",
        "branch",
        "scgpa",
        "honorsDept",
        "minorsDept",
    )
    ordering = ["-batchCode", "rollno"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("upload-csv/", self.upload_csv)]
        return my_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            batchCode = request.POST.get("batchCode")
            print(batchCode)
            field_mappings = [
                (0, "rollno"),
                (1, "name"),
                (2, "branch"),
                (3, "email"),
                (4, "phone"),
                (5, "total_credits"),
                (6, "total_grade"),
                (7, "scgpa"),
            ]

            upload_data_from_csv(request, UserData, batchCode, field_mappings)

        form = CsvImportForm()
        body = {"form": form}
        return render(request, "admin/upload-csv.html", body)


class HonorsModelControl(admin.ModelAdmin):
    list_display = ["rollno", "dept", "scgpa", "selectedDept"]
    ordering = ["dept", "-scgpa"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("filterHonors/", self.filterHonors),
            path("uploadHonors/", self.uploadHonors),
            path("downloadHonorsData/", self.download_csv),
        ]
        return my_urls + urls

    def uploadHonors(self, request):
        if request.method == "POST":
            batchCode = request.POST.get("batchCode")
            field_mappings = [
                (0, "rollno"),
                (1, "dept"),
                (2, "scgpa"),
            ]

            upload_data_from_csv(request, HonorsModel, batchCode, field_mappings)

        form = CsvImportForm()
        body = {"form": form}
        return render(request, "admin/upload-honors.html", body)

    def filterHonors(self, request):
        if request.method == "POST":
            unique_depts = HonorsModel.objects.values_list("dept", flat=True).distinct()
            try:
                top_records_rollno = []
                for dept in unique_depts:
                    top_records = HonorsModel.objects.filter(dept=dept).order_by(
                        "-scgpa"
                    )[:FILTERNUMBER]
                    top_record_ids = top_records.values_list("rollno", flat=True)
                    top_records_rollno.extend(top_record_ids)

                    for index, record in enumerate(top_records, start=1):
                        try:
                            UserData.objects.get(
                                rollno=record.rollno
                            ).update_honors_dept(dept)
                        except Exception as e:
                            print(f"{record.rollno} {e}")
                        record.selectedDept = f"{dept}"
                        record.save()

                HonorsModel.objects.exclude(rollno__in=top_records_rollno).delete()
                MinorsModel.objects.filter(rollno__in=top_records_rollno).delete()

                return redirect("/admin/AdminControl/honorsmodel/")
            except Exception as e:
                print(e)
        return render(request, "admin/filterHonors.html")

    def download_csv(self, request):
        if request.method == "POST":
            unique_depts = HonorsModel.objects.values_list("dept", flat=True).distinct()
            file_path = f"honors.csv"
            with open(file_path, "w", newline="") as csvfile:
                for selected_dept in unique_depts:
                    writer = csv.writer(csvfile)
                    writer.writerow(
                        [
                            selected_dept,
                        ]
                    )
                    honors_data = HonorsModel.objects.filter(selectedDept=selected_dept)

                    roll_numbers = [honors.rollno for honors in honors_data]
                    for roll_number in roll_numbers:
                        writer.writerow(["", roll_number])

            file_response = FileResponse(open(file_path, "rb"))
            file_response["Content-Disposition"] = f'attachment; filename="{file_path}"'
            return file_response

        return render(request, "admin/downloadCsv.html")


class MinorsModelControl(admin.ModelAdmin):
    list_display = [
        "rollno",
        "courseChoice1",
        "courseChoice2",
        "scgpa",
        "selectedDept",
    ]
    ordering = ["rollno", "-scgpa", "courseChoice1"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("filterMinors/", self.filterMinors),
            path("uploadMinors/", self.uploadMinors),
            path("downloadMinorsData/", self.download_csv),
        ]
        return my_urls + urls

    def uploadMinors(self, request):
        if request.method == "POST":
            batchCode = request.POST.get("batchCode")
            field_mappings = [
                (0, "rollno"),
                (1, "courseChoice1"),
                (2, "courseChoice2"),
                (3, "scgpa"),
            ]

            upload_data_from_csv(request, MinorsModel, batchCode, field_mappings)

        form = CsvImportForm()
        body = {"form": form}
        return render(request, "admin/upload-minors.html", body)

    def filter(self, available, unique_depts, courseChoice):
        try:
            top_records_rollno = []
            for dept in unique_depts:
                filter_condition = {courseChoice: dept, "selectedDept": None}
                if available[dept] > 0:
                    top_records = MinorsModel.objects.filter(
                        **filter_condition
                    ).order_by("-scgpa")[: available[dept]]

                    top_record_ids = top_records.values_list("rollno", flat=True)
                    top_records_rollno.extend(top_record_ids)
                    available[dept] = (
                        available[dept] - len(top_records_rollno)
                        if available[dept] - len(top_records_rollno) > 0
                        else 0
                    )

                    for record in top_records:
                        try:
                            UserData.objects.get(
                                rollno=record.rollno
                            ).update_minors_dept(dept)
                        except Exception as e:
                            print(f"{record.rollno} {e}")
                        record.selectedDept = f"{dept}"
                        record.save()

        except Exception as e:
            print(e)

    def filterMinors(self, request):
        if request.method == "POST":
            choice1_depts = MinorsModel.objects.values_list(
                "courseChoice1", flat=True
            ).distinct()
            choice2_depts = MinorsModel.objects.values_list(
                "courseChoice2", flat=True
            ).distinct()
            choice2_depts = [dept for dept in choice2_depts if dept != None]

            available = {
                "CSE": FILTERNUMBER,
                "ECE": FILTERNUMBER,
                "IT": FILTERNUMBER,
                "CIVIL": FILTERNUMBER,
                "MECH": FILTERNUMBER,
                "MET": FILTERNUMBER,
                "EEE": FILTERNUMBER,
            }
            self.filter(available, choice1_depts, "courseChoice1")
            self.filter(available, choice2_depts, "courseChoice2")
            MinorsModel.objects.filter(selectedDept=None).delete()
            return redirect("../")

        return render(request, "admin/filterMinors.html")

    def download_csv(self, request):
        if request.method == "POST":
            unique_depts = MinorsModel.objects.values_list(
                "selectedDept", flat=True
            ).distinct()
            unique_depts = [dept for dept in unique_depts if dept != None]
            file_path = f"minors.csv"
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Minors Data"])
                for selected_dept in unique_depts:
                    writer.writerow(
                        [
                            selected_dept,
                        ]
                    )
                    minors_data = MinorsModel.objects.filter(selectedDept=selected_dept)

                    roll_numbers = [minors.rollno for minors in minors_data]
                    for roll_number in roll_numbers:
                        writer.writerow(["", roll_number])

            file_response = FileResponse(open(file_path, "rb"))
            file_response["Content-Disposition"] = f'attachment; filename="{file_path}"'
            return file_response

        return render(request, "admin/downloadCsv.html")


admin.site.register(UserData, UserDataControl)
admin.site.register(HonorsModel, HonorsModelControl)
admin.site.register(MinorsModel, MinorsModelControl)
