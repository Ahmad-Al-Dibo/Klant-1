# core/context_processors.py
from django.conf import settings

def site_config(request):
    """
    Adds site configuration to template context
    """
    return {
        'site_config': {
            'COMPANY_NAME': getattr(settings, 'COMPANY_NAME', 'Company Services'),
            'ENABLE_SOCIAL_LOGIN': getattr(settings, 'ENABLE_SOCIAL_LOGIN', False),
            'ENABLE_GOOGLE_LOGIN': getattr(settings, 'ENABLE_GOOGLE_LOGIN', False),
            'ENABLE_FACEBOOK_LOGIN': getattr(settings, 'ENABLE_FACEBOOK_LOGIN', False),
            'SITE_URL': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'SUPPORT_EMAIL': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com'),
            'PHONE_NUMBER': getattr(settings, 'PHONE_NUMBER', '+1234567890'),
            'ADDRESS': getattr(settings, 'ADDRESS', ''),
        }
    }

def current_year(request):
    from datetime import datetime
    return {"current_year": datetime.now().year}


