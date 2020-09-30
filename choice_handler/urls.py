from django.urls import path
from . import views

urlpatterns = [
    path('meta', views.meta),
    path('youtube_url', views.youtube_url),
    path('file', views.file),
    path('detail', views.youtube_url)
]
