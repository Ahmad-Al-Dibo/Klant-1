# type: ignore[UndefinedVariable]

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _  # Dit is de belangrijke import!


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
    verbose_name = _('Projecten')
    
    def ready(self):
        pass