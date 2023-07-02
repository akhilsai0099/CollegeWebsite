from django.urls import path
from . import views

app_name = 'course_application'

urlpatterns = [
    # path('course-application-form',
    #      views.course_application, name='courseApplication'),
    path('onsubmit/', views.onsubmit, name='onsubmit'),
    path('login/', views.loginView, name='loginView'),
    path('logout/', views.logout, name='logout'),
    path('compare/', views.compare, name='compare'),
    path('create_users/', views.create_users, name='create_users'),
    path('', views.home, name='home'),
]
