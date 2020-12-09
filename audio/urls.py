from django.urls import path
from . import views

urlpatterns = [
    path('meta', views.meta),
    path('youtube', views.y_url),
    path('file', views.file),
    path('interval', views.interval),
    path('check', views.check)
]
