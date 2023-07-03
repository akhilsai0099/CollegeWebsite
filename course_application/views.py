from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.http import HttpResponseRedirect
from AdminControl.models import UserData
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from AdminControl.models import UserData, HonorsModel, MinorsModel


def logout(request):
    auth.logout(request)
    return redirect('/')


def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username == "" and password == "":
            messages.error(request, "Username and password cannot be empty")
        else:

            user = auth.authenticate(
                request, username=username, password=password)

            if user is not None:
                auth.login(request, user=user)
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'Invalid username or password')
                return HttpResponseRedirect(request.path_info)

    # Render the login form
    return render(request, 'login.html')


@login_required
def compare(request):

    user = request.user
    if user:
        student = UserData.objects.get(rollno=user.username)
        studentname = student.name
        studentbranch = student.branch
        studentcgpa = student.scgpa
        studentroll = student.rollno
        studentYear = 23 - int(student.batchCode)
        return render(request, 'mainpage.html', {'name': studentname, 'branch': studentbranch, 'rollno': studentroll, 'cgpa': studentcgpa, 'year': studentYear})


def onsubmit(request):
    if request.method == 'POST':
        cgpa = float(request.POST.get("cgpa", '0.00'))
        appliedForHonors = request.POST.get("AFH")
        appliedForMinors = request.POST.get("AFM")

        student = request.user
        studentdata = UserData.objects.get(rollno=student.username)
        if cgpa >= 8.0 and appliedForHonors:
            try:

                data, created = HonorsModel.objects.update_or_create(
                    rollno=studentdata.rollno,
                    defaults={
                        'dept': studentdata.branch,
                        'scgpa': studentdata.scgpa,
                    }
                )
                if created:
                    message = f"{student.first_name} applied successfully!"
                    messages.success(request, message)
                    print(f"Changes submitted")
                else:
                    print(f"Applied for the course {cgpa}")
                return redirect('/')
            except Exception as e:
                print(e)
                message = "unable to apply"
                messages.error(request, message)
                return render(request, 'mainpage.html', {'alerting': message})

        if cgpa >= 7.5 and appliedForMinors:
            try:
                choice1 = request.POST['choice1']
                choice2 = request.POST['choice2']

                data, created = MinorsModel.objects.update_or_create(
                    rollno=studentdata.rollno,
                    defaults={
                        'scgpa': studentdata.scgpa,
                    }
                )

                if choice2 != "none":
                    # Only include choice2 in the database update if it is not None
                    data.courseChoice2 = choice2
                data.courseChoice1 = choice1
                data.save()

                if created:
                    message = f"{student.first_name} applied successfully!"
                    messages.success(request, message)
                    print(f"Changes submitted")
                else:
                    print(f"Applied for the course {cgpa}")
                return redirect('/')
            except Exception as e:
                print(e)
                message = "unable to apply"
                messages.error(request, message)
                return render(request, 'mainpage.html', {'alerting': message})


def home(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'base.html', context)
