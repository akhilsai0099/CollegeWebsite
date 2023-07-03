from django.urls import path
from . import views

app_name = 'course_application'

urlpatterns = [
    path('onsubmit/', views.onsubmit, name='onsubmit'),
    path('login/', views.loginView, name='loginView'),
    path('logout/', views.logout, name='logout'),
    path('compare/', views.compare, name='compare'),
    path('', views.home, name='home'),
]
