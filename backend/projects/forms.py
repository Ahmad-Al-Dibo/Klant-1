from django import forms
from .models import ProjectTag

class ProjectTagForm(forms.ModelForm):
    class Meta:
        model = ProjectTag
        fields = "__all__"