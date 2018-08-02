from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import login, logout

urlpatterns = [
    path('', include('alhopics.urls')),
    path('login/', login, {'template_name': 'alhopics/login.html'}, name='login'),
    path('logout/', logout, {'template_name': 'alhopics/logout.html'}),
    path('admin/', admin.site.urls),
]
