from django.urls import path
from .views import *
from django.views.generic import TemplateView
from stream_tweet.views import create_stream

urlpatterns = [
    path('', HomeView.as_view()),
    path('<int:page>', HomeView.as_view(), name='home'),
    path('manage/', manage, name='manage'),
    path('update/<str:id>/', update, name='update'),
    path('delete/<str:id>/', delete, name='delete'),
    path('detail/<str:id>/', detail, name='detail')
]
