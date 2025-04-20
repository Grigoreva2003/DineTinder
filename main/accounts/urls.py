from django.urls import path
from . import views

urlpatterns = [
    path('modify/', views.modify_data)
]