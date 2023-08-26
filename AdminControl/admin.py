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

FILTERNUMBER = 22
WAITING_NUMBER = 3


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
            csv_file = request.FILES.get("csv_upload")
            batchCode = request.POST["batchCode"]
            # print(batchCode)

            if not csv_file:
                messages.warning(request, "Please upload a CSV file")
                return HttpResponseRedirect(request.path_info)

            if not csv_file.name.endswith(".csv"):
                messages.warning(request, "Please upload a CSV file")
                return HttpResponseRedirect(request.path_info)

            decoded_file = csv_file.read().decode("utf-8").splitlines()
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
                    created = UserData.objects.update_or_create(
                        rollno=rollno,
                        defaults={
                            "name": name,
                            "branch": branch,
                            "email": email,
                            "phone": phone,
                            "scgpa": scgpa,
                            "total_credits": total_credits,
                            "total_grade": total_grade,
                            "batchCode": batchCode,
                        },
                    )

                    if created:
                        User.objects.create_user(
                            username=rollno, password=phone, first_name=name
                        )
                        messages.success(request, f"Data added for Roll No: {rollno}")
                    else:
                        messages.success(request, f"Data updated for Roll No: {rollno}")
                except Exception as e:
                    messages.error(
                        request,
                        f"Error updating/adding data for Roll No: {rollno} - {str(e)}",
                    )

            messages.success(request, "Data has been uploaded from the CSV file")
            return HttpResponseRedirect(request.path_info)

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

    def filterHonors(
        self, request
    ):  # sourcery skip: extract-method, remove-redundant-fstring
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
                    for record in top_records:
                        try:
                            UserData.objects.get(
                                rollno=record.rollno
                            ).update_honors_dept(dept)

                        except Exception as e:
                            print(f"{record.rollno} {e}")

                        record.selectedDept = f"{dept}"
                        record.save()
                    print("students who are selected are....")
                    for students in top_records:
                        print(students.rollno)

                # for waiting lists....
                waiting_list_rollno = []
                for dept in unique_depts:
                    waiting_list_records = HonorsModel.objects.filter(
                        dept=dept, selectedDept=None
                    ).order_by("-scgpa")[:WAITING_NUMBER]
                    waiting_list_rollno.extend(
                        waiting_list_records.values_list("rollno", flat=True)
                    )
                    for students in waiting_list_records:
                        try:
                            UserData.objects.get(
                                rollno=students.rollno
                            ).update_honors_dept("WL")
                        except Exception as e:
                            print(f"{students.rollno} {e}")

                        students.waiting_list = "WL"
                        students.save()
                    print("students who are in waiting lists are...")
                    for students in waiting_list_records:
                        print(students.rollno)

                HonorsModel.objects.exclude(rollno__in=top_records_rollno).delete()
                MinorsModel.objects.filter(rollno__in=top_records_rollno).delete()
                # HonorsModel.objects.all().delete()
                messages.success(request, "Data has been filtered")
                return redirect("/admin/AdminControl/honorsmodel/")
            except Exception as e:
                print(e)
                messages.error(request, f"Hello")

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
        "courseChoice3",
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
                (3, "courseChoice3"),
                (4, "scgpa"),
            ]

            upload_data_from_csv(request, MinorsModel, batchCode, field_mappings)

        form = CsvImportForm()
        body = {"form": form}
        return render(request, "admin/upload-minors.html", body)

    def filterMinors(self, request):
        if request.method == "POST":
            is_honors_not_filterd = HonorsModel.objects.filter(
                selectedDept=None
            ).exists()
            if not is_honors_not_filterd:
                available = {
                    "CSE": FILTERNUMBER,
                    "ECE": FILTERNUMBER,
                    "IT": FILTERNUMBER,
                    "CIVIL": FILTERNUMBER,
                    "MECH": FILTERNUMBER,
                    "MET": FILTERNUMBER,
                    "EEE": FILTERNUMBER,
                }
                waiting = {
                    "CSE": WAITING_NUMBER,
                    "ECE": WAITING_NUMBER,
                    "IT": WAITING_NUMBER,
                    "CIVIL": WAITING_NUMBER,
                    "MECH": WAITING_NUMBER,
                    "MET": WAITING_NUMBER,
                    "EEE": WAITING_NUMBER,
                }
                students_order = MinorsModel.objects.all().order_by("-scgpa")
                try:
                    for student in students_order:
                        if student.selectedDept is None:
                            choices = [
                                student.courseChoice1.strip()
                                if student.courseChoice1
                                else None,
                                student.courseChoice2.strip()
                                if student.courseChoice2
                                else None,
                                student.courseChoice3.strip()
                                if student.courseChoice3
                                else None,
                            ]

                            # strip is a function used to remove the trailing spaces and leading spaces
                            for choice in choices:
                                try:
                                    if student.selectedDept is None:
                                        if available[choice] > 0:
                                            try:
                                                student.selectedDept = choice
                                                user = UserData.objects.get(
                                                    rollno=student.rollno
                                                )
                                                user.minorsDept = choice
                                                user.save()
                                                student.save()
                                                available[choice] -= 1
                                                print(available)
                                            except Exception as e:
                                                print(f"{student.rollno} {e}")
                                        else:
                                            try:
                                                if (
                                                    waiting[choice] > 0
                                                    and student.waiting_list1 is None
                                                ):
                                                    student.waiting_list1 = choice
                                                    waiting[choice] -= 1
                                                    student.save()
                                                elif (
                                                    waiting[choice] > 0
                                                    and student.waiting_list2 is None
                                                ):
                                                    student.waiting_list2 = choice
                                                    waiting[choice] -= 1
                                                    student.save()
                                                elif (
                                                    waiting[choice] > 0
                                                    and student.waiting_list3 is None
                                                ):
                                                    student.waiting_list3 = choice
                                                    waiting[choice] -= 1
                                                    student.save()
                                            except Exception as e:
                                                print(f"{student.rollno} {e}")

                                except Exception as e:
                                    print(f"{student.rollno} {e}")
                    students_order = MinorsModel.objects.filter(
                        selectedDept=None
                    ).order_by("-scgpa")
                except Exception as e:
                    messages.error(f"{student.rollno} {e}")

                MinorsModel.objects.filter(selectedDept=None).delete()
                #MinorsModel.objects.all().delete()
                messages.success(request, "Data has been filtered successfully")
            else:
                messages.error(
                    request,
                    "You have not filterd Honors data, Please filter Honors data before filtering minors data",
                )
        return redirect("/admin/AdminControl/minorsmodel")

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
