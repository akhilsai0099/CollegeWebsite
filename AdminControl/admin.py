from django.contrib import admin, messages
from .models import UserData, HonorsModel, MinorsModel, BatchCode
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponseRedirect
from .forms import BatchForm
from .views import upload_data_from_csv
import csv
from django.db.models import Q

FILTERNUMBER = 21
WAITING_NUMBER = 3


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()
    csv_upload.label = "Upload a CSV file"
    batchCode = forms.ModelChoiceField(queryset=BatchCode.objects.all(), empty_label=None)
    batchCode.label = "Select the batchCode "



class UserDataControl(admin.ModelAdmin):
    list_display = (
        "batchCode",
        "rollno",
        "name",
        "branch",
        "formatted_scgpa",
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
            #print(batchCode)

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
                sgpa = row[7]
                credits = row[5]
                total_grade = row[6]

                try:
                    userdata=UserData.objects.get(rollno=rollno)
                    scgpa=((float(userdata.scgpa)*float(userdata.total_credits))+(float(sgpa)*float(credits)))/(float(userdata.total_credits)+float(credits))
                    total_credits=float(userdata.total_credits)+float(credits)

                    userdata.scgpa=scgpa
                    userdata.total_credits=total_credits

                    userdata.save()

                    messages.success(request, f"Data updated for Roll No: {rollno}")
                except Exception as e:
                    UserData.objects.create(
                        rollno=rollno,
                        name=name,
                        branch=branch,
                        email=email,
                        phone=phone,
                        scgpa=sgpa,
                        total_credits=credits,
                        total_grade=total_grade,
                        batchCode=batchCode
                    )
                    User.objects.create_user(
                        username=rollno, password=phone, first_name=name,email=email
                    )
                    messages.success(request, f"Data added for Roll No: {rollno}")


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
    list_display = ['batchCode',"rollno", "dept", "scgpa", "selectedDept","waiting_list"]
    ordering = ["dept", "-scgpa"]
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("filterHonors/", self.filterHonors),
            path("uploadHonors/", self.uploadHonors),
            path("downloadHonorsData/", self.download_csv),
            path("downloadHonorsWaitlist/", self.download_waitlist_csv),
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
            batch = request.POST['batchCode']
            unique_depts = HonorsModel.objects.values_list("dept", flat=True).distinct()
            try:
                top_records_rollno = []
                for dept in unique_depts:
                    top_records = HonorsModel.objects.filter(batchCode=batch, dept=dept).order_by(
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
                        #for waiting list students
                waiting_list_rollno = []
                for dept in unique_depts:
                    waiting_list_records = HonorsModel.objects.filter(
                        dept=dept, selectedDept=None
                    ).order_by("-scgpa")[:WAITING_NUMBER]
                    waiting_list_rollno.extend(
                        waiting_list_records.values_list("rollno", flat=True)
                    )
                    for students in waiting_list_records:
                        students.waiting_list = "WL"
                        students.save()

                MinorsModel.objects.filter( batchCode = batch, rollno__in=top_records_rollno).delete()
                top_records_rollno.extend(waiting_list_rollno)
                HonorsModel.objects.filter(batchCode = batch).exclude( rollno__in=top_records_rollno).delete()

                messages.success(request, "Data has been filtered")
                return redirect("/admin/AdminControl/honorsmodel/")
            except Exception as e:
                print(e)
                messages.error(request, f"Error Occured {e}")
        form = BatchForm()
        context = {'form': form}
        return render(request, "admin/filterHonors.html",context)

    def download_csv(self, request):
        if request.method == "POST":
            batch = request.POST['batchCode']
            unique_depts = HonorsModel.objects.values_list("dept", flat=True).distinct()
            file_path = f"Honors {batch}.csv"
            with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                for selected_dept in unique_depts:
                    writer = csv.writer(csvfile)
                    writer.writerow(
                        [
                            selected_dept,
                        ]
                    )
                    honors_data = HonorsModel.objects.filter(selectedDept=selected_dept, batchCode= batch)

                    roll_numbers = [honors.rollno for honors in honors_data]
                    for roll_number in roll_numbers:
                        writer.writerow(["", roll_number])

            file_response = FileResponse(open(file_path, "rb"))
            file_response["Content-Disposition"] = f'attachment; filename="{file_path}"'
            return file_response

        form = BatchForm()
        return render(request, "admin/downloadCsv.html",{'form':form})

    def download_waitlist_csv(self, request):
        if request.method == "POST":
            batch = request.POST['batchCode']
            unique_depts = HonorsModel.objects.values_list("dept", flat=True).distinct()
            file_path = f"Honors_waitingList {batch}.csv"
            with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                for selected_dept in unique_depts:
                    writer = csv.writer(csvfile)
                    writer.writerow(
                        [
                            selected_dept,
                        ]
                    )
                    honors_data = HonorsModel.objects.filter(waiting_list="WL", batchCode = batch,dept=selected_dept)

                    roll_numbers = [honors.rollno for honors in honors_data]
                    for roll_number in roll_numbers:
                        writer.writerow(["", roll_number])

            file_response = FileResponse(open(file_path, "rb"))
            file_response["Content-Disposition"] = f'attachment; filename="{file_path}"'
            return file_response

        form = BatchForm()
        return render(request, "admin/downloadCsv.html",{'form':form})


class MinorsModelControl(admin.ModelAdmin):
    list_display = [
        'batchCode',
        "rollno",
        "courseChoice1",
        "courseChoice2",
        "courseChoice3",
        "scgpa",
        "selectedDept",
        "waiting_list1",
        "waiting_list2",
        "waiting_list3",
    ]
    ordering = ["rollno", "-scgpa", "courseChoice1"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("filterMinors/", self.filterMinors),
            path("uploadMinors/", self.uploadMinors),
            path("downloadMinorsData/", self.download_csv),
            path("downloadMinorsWaitlist/", self.download_minors_csv),
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

    # def filter(self, available, unique_depts, courseChoice):
    #     try:
    #         top_records_rollno = []
    #         for dept in unique_depts:
    #             filter_condition = {courseChoice: dept, "selectedDept": None}
    #             if available[dept] > 0:
    #                 top_records = MinorsModel.objects.filter(
    #                     **filter_condition
    #                 ).order_by("-scgpa")[: available[dept]]

    #                 top_record_ids = top_records.values_list("rollno", flat=True)
    #                 top_records_rollno.extend(top_record_ids)
    #                 available[dept] = (
    #                     available[dept] - len(top_records_rollno)
    #                     if available[dept] - len(top_records_rollno) > 0
    #                     else 0
    #                 )

    #                 for record in top_records:
    #                     try:
    #                         UserData.objects.get(
    #                             rollno=record.rollno
    #                         ).update_minors_dept(dept)
    #                     except Exception as e:
    #                         print(f"{record.rollno} {e}")
    #                     record.selectedDept = f"{dept}"
    #                     record.save()

    #     except Exception as e:
    #         print(e)

    # def filterMinors(self, request):
    #     if request.method == "POST":
    #         is_honors_not_filterd = HonorsModel.objects.filter(
    #             selectedDept=None
    #         ).exists()
    #         if not is_honors_not_filterd:
    #             choice1_depts = MinorsModel.objects.values_list(
    #                 "courseChoice1", flat=True
    #             ).distinct()
    #             choice2_depts = MinorsModel.objects.values_list(
    #                 "courseChoice2", flat=True
    #             ).distinct()
    #             choice2_depts = [dept for dept in choice2_depts if dept != None]

    #             available = {
    #                 "CSE": FILTERNUMBER,
    #                 "ECE": FILTERNUMBER,
    #                 "IT": FILTERNUMBER,
    #                 "CIVIL": FILTERNUMBER,
    #                 "MECH": FILTERNUMBER,
    #                 "MET": FILTERNUMBER,
    #                 "EEE": FILTERNUMBER,
    #             }
    #             self.filter(available, choice1_depts, "courseChoice1")
    #             self.filter(available, choice2_depts, "courseChoice2")
    #             MinorsModel.objects.filter(selectedDept=None).delete()
    #             messages.success(request, "Data has been filtered")
    #         else:
    #             messages.error(
    #                 request,
    #                 "You have not filterd Honors data, Please filter Honors data before filtering minors data",
    #             )
    #     return redirect("/admin/AdminControl/minorsmodel")

    def filterMinors(self, request):
        if request.method == "POST":
            batch = request.POST['batchCode']
            is_honors_not_filterd = HonorsModel.objects.filter(
                Q(batchCode = batch,selectedDept=None) 
            ).filter(Q(waiting_list=None)).exists()
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
                #students_order = MinorsModel.objects.all().order_by("-scgpa")
                students_order = MinorsModel.objects.filter(batchCode = batch).order_by("-scgpa")
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
                                            except Exception as e:
                                                print(f"{student.rollno} {e}")
                                        else:
                                            pass
                                except Exception as e:
                                    print(f"{student.rollno} {e}")

                            for choice in choices:
                                try:
                                    if student.selectedDept is None :
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
                                        print(f"{waiting} for {student.rollno}")
                                    else :
                                        pass
                                except Exception as e:
                                    print(f"{student.rollno} {e}")


                    students_order = MinorsModel.objects.filter(
                        selectedDept=None
                    ).order_by("-scgpa")
                except Exception as e:
                    messages.error(f"{student.rollno} {e}")
                print(batch)
                # MinorsModel.objects.filter(batchCode= batch,selectedDept = None).delete()
                #MinorsModel.objects.all().delete()
                MinorsModel.objects.filter(
                    batchCode=batch
                ).exclude(
                    Q(selectedDept__isnull=False) | 
                    Q(waiting_list1__isnull=False) | 
                    Q(waiting_list2__isnull=False) | 
                    Q(waiting_list3__isnull=False)
                ).delete()
                messages.success(request, "Data has been filtered successfully")
            else:
                messages.error(
                    request,
                    "You have not filterd Honors data, Please filter Honors data before filtering minors data",
                )
        form = BatchForm()
        context = {'form': form}
        return render(request, "admin/filterMinors.html",context)


    def download_csv(self, request):
        if request.method == "POST":
            batch = request.POST['batchCode']
            unique_depts = MinorsModel.objects.values_list(
                "selectedDept", flat=True
            ).distinct()
            unique_depts = [dept for dept in unique_depts if dept != None]
            file_path = f"Minors {batch}.csv"
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Minors Data"])
                for selected_dept in unique_depts:
                    writer.writerow(
                        [
                            selected_dept,
                        ]
                    )
                    minors_data = MinorsModel.objects.filter(selectedDept=selected_dept, batchCode=batch)

                    roll_numbers = [minors.rollno for minors in minors_data]
                    for roll_number in roll_numbers:
                        writer.writerow(["", roll_number])

            file_response = FileResponse(open(file_path, "rb"))
            file_response["Content-Disposition"] = f'attachment; filename="{file_path}"'
            return file_response

        form = BatchForm()
        return render(request, "admin/downloadCsv.html",{'form':form})

    def download_minors_csv(self, request):
        if request.method == "POST":
            batch = request.POST['batchCode']
            unique_depts = MinorsModel.objects.values_list(
                "selectedDept", flat=True
            ).distinct()
            unique_depts = [dept for dept in unique_depts if dept != None]
            file_path = f"Minors_waitlist {batch}.csv"
            with open(file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Minors Data"])
                for selected_dept in unique_depts:
                    writer.writerow(
                        [
                            selected_dept,
                        ]
                    )
                    minors_data = MinorsModel.objects.filter(
                                    Q(waiting_list1=selected_dept) |
                                    Q(waiting_list2=selected_dept) |
                                    Q(waiting_list3=selected_dept) &
                                    Q(batchCode = batch))

                    roll_numbers = [minors.rollno for minors in minors_data]
                    for roll_number in roll_numbers:
                        writer.writerow(["", roll_number])

            file_response = FileResponse(open(file_path, "rb"))
            file_response["Content-Disposition"] = f'attachment; filename="{file_path}"'
            return file_response

        form = BatchForm()
        return render(request, "admin/downloadCsv.html",{'form':form})



class Batch(admin.ModelAdmin):
    pass

admin.site.register(UserData, UserDataControl)
admin.site.register(HonorsModel, HonorsModelControl)
admin.site.register(MinorsModel, MinorsModelControl)
admin.site.register(BatchCode, Batch)
