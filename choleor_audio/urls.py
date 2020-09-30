from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('choice/', include('choice_handler.urls')),
    path('score/', include('score.urls')),
    path('admin/', admin.site.urls)
]
