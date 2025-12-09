from django.urls import path
from . import views

urlpatterns = [
    path('projects_list/', views.project_list, name='project_list'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
]
