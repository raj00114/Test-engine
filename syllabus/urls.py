from django.urls import path

from . import views

urlpatterns = [
    path("", views.syllabus_list, name="syllabus_list"),
]
