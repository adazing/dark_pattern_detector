
from django.contrib import admin
from django.urls import path
from api.views import *

urlpatterns = [
    path("check/", check_elements, name="check_elements"),
]
