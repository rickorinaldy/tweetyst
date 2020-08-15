from django.urls import path
from .views import *

urlpatterns=[
    path('<str:id>/<str:nama>/<int:bulan1>/<int:bulan2>/<int:tahun>', show_data, name='show')
]
