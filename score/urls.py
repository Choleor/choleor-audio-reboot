from django.urls import path
from . import views

urlpatterns = [
    path('similarity', views.similarity_score),
    path('amplitude', views.avg_amplitude_list)
]