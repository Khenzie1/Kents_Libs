# django_price_comparer/price_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
