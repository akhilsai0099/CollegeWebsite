from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

# Create your views here.


def logout(request):
    auth.logout(request)
    return redirect("/")


def login(request):
    next_url = request.GET.get("next")
    if next_url:
        request.session["next_url"] = next_url
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if not username  or not password :
            messages.error(request, "Username and password cannot be empty")
        else:
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user=user)
                print(next_url)
                next_url = request.session.get("next_url")
                if next_url:
                    del request.session["next_url"]
                    return redirect(next_url)
                request.session["roll_number"] = username
                return redirect("/")
            else:
                messages.error(request, "Invalid username or password")
                return redirect(request.path_info)

    # Render the login form
    return render(request, "login.html", {"messages": messages.get_messages(request)})
