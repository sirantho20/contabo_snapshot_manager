from django.urls import path
from . import views

app_name = 'snapshots'

urlpatterns = [
    path('', views.home, name='home'),
    path('status/', views.status, name='status'),
] 