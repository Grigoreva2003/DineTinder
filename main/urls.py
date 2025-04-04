"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from main.views import landing_page, vk_login_page, home_page, error_page, vk_authenticate, PlaceListView, \
    PlaceFilterView, simple_login_page, get_recommendation_page, search_places_page

urlpatterns = [
    path('admin/', admin.site.urls),

    path('places/', PlaceFilterView.as_view(), name='places-list'),
    path('carousel/', include('main.carousel.urls')),
    path('vk/auth/', vk_authenticate),

    path('', landing_page),
    path('home/', home_page),
    path('login/vk', vk_login_page),
    path('login/', simple_login_page),
    path('get_recommendation/', get_recommendation_page),
    path('search_places/', search_places_page),
    path('error/', error_page),
    # path('accounts/', include('accounts.urls')),
    # path('recommendations/', include('recommendations.urls')),
    # path('history/', include('history.urls')),
]
