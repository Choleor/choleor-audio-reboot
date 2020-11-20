from django.urls import path
from . import views

urlpatterns = [
    path('meta', views.meta),
    path('youtube', views.url),
    path('file', views.file),
    # path('detail', views.interval_choice),
]
