from django.urls import path
from . import views

urlpatterns = [
    path('favorite/<int:place_id>/', views.mark_favorite, name='mark_favorite'),
    path('interested/<int:place_id>/', views.mark_interested, name='mark_interested'),
    path('not-interested/<int:place_id>/', views.mark_not_interested, name='mark_not_interested'),
    path('blacklist/<int:place_id>/', views.mark_blacklist, name='mark_blacklist'),
    path('check-favorite/<int:place_id>/', views.check_favorite, name='check_favorite'),
    path('shown/<int:place_id>/', views.mark_shown, name='mark_shown'),
]