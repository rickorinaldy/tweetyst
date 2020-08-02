from django.urls import path
from . import views

urlpatterns = [
    path('online/', views.online_stream, name='online'),
    path('file/', views.file_stream, name='file')
]
