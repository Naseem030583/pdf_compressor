from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('result/<int:pk>/', views.result, name='result'),
    path('download/<int:pk>/', views.download, name='download'),
    path('history/', views.history, name='history'),
]
