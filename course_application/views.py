from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from AdminControl.models import UserData
from django.contrib.auth.decorators import login_required
from AdminControl.models import UserData, HonorsModel, MinorsModel
from datetime import datetime


@login_required
def compare(request):
    user = request.user
    if user:
        try:
            student = UserData.objects.filter(rollno=user.username)[0]
            studentname = student.name
            studentbranch = student.branch
            studentcgpa = student.scgpa
            studentroll = student.rollno
            studentYear = int(datetime.today().strftime("%y")) - int(student.batchCode)
            return render(
                request,
                "mainpage.html",
                {
                    "name": studentname,
                    "branch": studentbranch,
                    "rollno": studentroll,
                    "cgpa": studentcgpa,
                    "year": studentYear,
                },
            )
        except Exception as e:
            print(e)

        return render(
            request,
            "mainpage.html",
        )


@login_required
def onsubmit(request):
    if request.method == "POST":
        cgpa = float(request.POST.get("cgpa", "0.00"))
        appliedForHonors = request.POST.get("AFH")
        appliedForMinors = request.POST.get("AFM")

        student = request.user
        studentdata = UserData.objects.get(rollno=student.username)
        honors = None
        minors = None
        if appliedForHonors and appliedForMinors:
            honors = applyHonors(request, studentdata, cgpa)
            minors = applyMinors(request, studentdata, cgpa)
            if honors == "Unable to submit" or minors == "Unable to submit":
                messages.error(
                    request,
                    f"{honors} for Honors Application, {minors} for Minors Application",
                )
            else:
                messages.success(
                    request,
                    f"{honors} for Honors Application, {minors} for Minors Application",
                )
        elif appliedForHonors and not appliedForMinors:
            honors = applyHonors(request, studentdata, cgpa)
            MinorsModel.objects.filter(rollno=student.username).delete()
            if honors == "Unable to submit":
                messages.error(request, f"{honors} for Honors Application")
            else:
                messages.success(request, f"{honors} for Honors Application")

        elif appliedForMinors and not appliedForHonors:
            minors = applyMinors(request, studentdata, cgpa)
            HonorsModel.objects.filter(rollno=student.username).delete()

            if minors == "Unable to submit":
                messages.error(request, f"{minors} for Minors Application")
            else:
                messages.success(request, f"{minors} for Minors Application")

        return render(
            request,
            "submitted.html",
        )


def applyHonors(request, studentdata, cgpa):
    if cgpa >= 8.0:
        try:
            data, created = HonorsModel.objects.update_or_create(
                rollno=studentdata.rollno,
                defaults={
                    "dept": studentdata.branch,
                    "scgpa": studentdata.scgpa,
                },
            )
            if created:
                return "Application submitted"
            else:
                return "Changes submitted"

        except Exception as e:
            return "Unable to submit"


def applyMinors(request, studentdata, cgpa):
    if cgpa >= 7.5:
        try:
            choice1 = request.POST["choice1"]
            choice2 = request.POST["choice2"]

            data, created = MinorsModel.objects.update_or_create(
                rollno=studentdata.rollno,
                defaults={
                    "scgpa": studentdata.scgpa,
                },
            )

            if choice2 != "None":
                # Only include choice2 in the database update if it is not None
                data.courseChoice2 = choice2
            else:
                data.courseChoice2 = None
            data.courseChoice1 = choice1
            data.save()

            if created:
                return "Application submitted"
            else:
                return "Changes submitted"
        except Exception as e:
            return "Unable to submit"


def home(request):
    user = request.user
    message = None
    honors_applied = HonorsModel.objects.filter(rollno=user.username)
    minors_applied = MinorsModel.objects.filter(rollno=user.username)
    if honors_applied.exists() and minors_applied.exists():
        message = f"You have applied for honors and minors in {minors_applied[0].courseChoice1}"
    elif honors_applied.exists():
        message = "You have applied for honors"
    elif minors_applied.exists():
        message = f"You have applied for Minors in {minors_applied[0].courseChoice1}"

    context = {"user": user, "message": message}
    return render(request, "base.html", context)
