
from django.contrib import admin
from django.urls import path
from api.views import *

urlpatterns = [
    path("check/", check_elements, name="check_elements"),
    path("", home, name="home"),
    path("articles/1/", article_view, name="article_view"),
    # path("articles/", articles_list, name="articles_list"),
    path("about/", about, name="about"),
    path("demo/", demo_view, name="demo"),
]
