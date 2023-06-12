from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render


def home_view(request):
    return render(request, 'home.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram/', include('totosha.urls')),
    path('', home_view),
]


