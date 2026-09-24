from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("tests/", views.test_list, name="test_list"),
    path("tests/<int:pk>/", views.take_test, name="take_test"),
]