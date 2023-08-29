from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from AdminControl.models import UserData
from .helpers import send_forget_password_mail
import uuid
from .models import *
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
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

        if username == "" and password == "":
            messages.error(request, "Username and password cannot be empty")
        else:
            user = auth.authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user=user)
                next_url = request.session.get("next_url")
                if next_url:
                    del request.session["next_url"]
                    return redirect(next_url)

                return HttpResponseRedirect("/")
            else:
                messages.error(request, "Invalid username or password")
                return redirect(request.path_info)

    # Render the login form
    return render(request, "login.html", {"messages": messages.get_messages(request)})



def ResetPassword(request , token):
    context = {}
    
    
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        context = {'user_id' : profile_obj.user.id}
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            
            if user_id is  None:
                messages.success(request, 'No user id found.')
                return redirect(f'/auth/reset_password/{token}/')
            
            if new_password == "" or confirm_password == "":
                messages.success(request, "Please Enter the password ")
                return redirect(f'/auth/reset_password/{token}/')
            
                
            
            if  new_password != confirm_password:
                messages.success(request, 'Passwords do not match')
                return redirect(f'/auth/reset_password/{token}/')
                         
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('/auth/login')
            
            
            
        
        
    except Exception as e:
        print(e)
    return render(request , 'reset_password.html' , context)



def ForgetPassword(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        
        try:
            user_obj = User.objects.get(username=username)
            #print(user_obj)
            #print(user_obj.email)
        except User.DoesNotExist:
            messages.error(request, 'No user found with this username.')
            return redirect(request.path_info)
        
        try:
            profile_obj = Profile.objects.get(user=user_obj)
        except ObjectDoesNotExist:
            profile_obj = Profile.objects.create(user=user_obj, forget_password_token="")
        
        token = str(uuid.uuid4())
        profile_obj.forget_password_token = token
        profile_obj.save()
        
        send_forget_password_mail(user_obj.email,user_obj.first_name, token)
        messages.success(request, 'Reset password email sent')
        return redirect(request.path_info)
    else:
        return render(request, 'forget_password.html') 
    

#code for changing password
@login_required
def changepassword(request):
    return render(request,"changepwd.html")


@login_required
def changingpwd(request):
    if request.method == "POST":
        try:
            oldpassword = request.POST.get("oldpassword")
            newpass = request.POST.get("newpassword")
            newpass2 = request.POST.get("newpassword2")
            
            user = request.user
            if user.check_password(oldpassword) :
                if(newpass == newpass2):
                    user.set_password(newpass)
                    user.save()
                        
                    messages.success(request, "Password Changed")
                    return redirect('/auth/login')
                else:
                    messages.error(request,'New passwords are not matching')
            else:
                messages.error(request,"your old password is Incorrect")
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
        except Exception as e:
            messages.error(request,e)
    else:
        pass
    
    return render(request,"changepwd.html")