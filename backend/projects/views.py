from django.http import JsonResponse
from django.shortcuts import render
from .models import Project

# Create your views here.

def project_list(request):
    # reurn json response with list of projects
    projects_list = Project.objects.all().values('id', 'name', 'status', 'start_date', 'end_date', 'budget')
    return JsonResponse({'projects': list(projects_list)})

def project_detail(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        project_data = {
            'id': project.id,
            'name': project.name,
            'status': project.status,
            'start_date': project.start_date,
            'end_date': project.end_date,
            'budget': project.budget,
        }
        return JsonResponse({'project': project_data})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)