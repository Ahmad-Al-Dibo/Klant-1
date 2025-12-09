from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = _('Orders')
    
    def ready(self):
        """Import signals wanneer app ready is"""
        import orders.signals