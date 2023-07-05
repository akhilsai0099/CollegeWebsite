from django.urls import path
from . import views

app_name = "course_application"

urlpatterns = [
    path("onsubmit/", views.onsubmit, name="onsubmit"),
    path("compare/", views.compare, name="compare"),
    path("", views.home, name="home"),
]
