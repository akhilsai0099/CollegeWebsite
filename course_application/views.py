from django.shortcuts import render, redirect
from .forms import CourseApplicationForm
from django.contrib import messages, auth
from django.http import HttpResponseRedirect
from AdminControl.models import UserData
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


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
    print(user.username)
    if user:
        student = UserData.objects.get(rollno=user.username)
        studentname = student.name
        studentbranch = student.branch
        studentcgpa = student.scgpa
        studentroll = student.rollno
        return render(request, 'mainpage.html', {'name': studentname, 'branch': studentbranch, 'rollno': studentroll, 'cgpa': studentcgpa})


def onsubmit(request):
    if request.method == 'POST':
        cgpa = float(request.POST.get("cgpa", '0.00'))
        AFH = request.POST.get("AFH")

        if cgpa < 8.0 and AFH:
            result = "it wont occur"
            return render(request, "absent.html", {'result': result})

        elif cgpa >= 8.0 and AFH:
            return render(request, 'present.html')
    result = "sorry! you are unable to apply.."
    return render(request, 'mainpage.html', {'alerting': result})


def home(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'base.html', context)


def create_users(request):
    return redirect("http://www.google.com")
