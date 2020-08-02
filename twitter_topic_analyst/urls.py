"""twitter_topic_analyst URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from stream_tweet import views
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/home')),
    path('home/', include(('home.urls', 'home'), namespace='home')),
    path('analysis/', include(('analysis.urls', 'analysis'), namespace='analysis')),
    path('stream_tweet/', include(('stream_tweet.urls', 'stream_tweet'), namespace='stream')),
    path('admin/', admin.site.urls)
]
