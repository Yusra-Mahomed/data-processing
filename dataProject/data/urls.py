from django.urls import path
from . import views

app_name = 'data'

urlpatterns = [
       path('upload/', views.upload_file, name = 'file_upload'),
       path('override/', views.override_data_type, name='override'),
]