from django.urls import path
from . import views

app_name = "course_application"

urlpatterns = [
    path(
        "submissionStatus/",
        views.honorsMinorsFormSubmit,
        name="honorsMinorsFormSubmit",
    ),
    path(
        "honorsMinorsApplication/",
        views.honorsMinorsApplication,
        name="honorsMinorsApplication",
    ),
    path("", views.home, name="home"),
]
