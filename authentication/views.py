from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

# Create your views here.


def logout(request):
    auth.logout(request)
    return redirect("/")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if username == "" and password == "":
            messages.error(request, "Username and password cannot be empty")
        else:
            user = auth.authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user=user)
                return HttpResponseRedirect("/")
            else:
                messages.error(request, "Invalid username or password")
                return redirect(request.path_info)

    # Render the login form
    return render(request, "login.html", {"messages": messages.get_messages(request)})
