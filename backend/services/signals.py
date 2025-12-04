from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Service, ServiceCategory
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Service)
def generate_service_slug(sender, instance, **kwargs):
    """Genereer slug als deze niet bestaat"""
    if not instance.slug:
        instance.slug = slugify(instance.name)
        
        # Zorg voor unieke slug
        counter = 1
        original_slug = instance.slug
        while Service.objects.filter(slug=instance.slug).exists():
            instance.slug = f"{original_slug}-{counter}"
            counter += 1


@receiver(pre_save, sender=ServiceCategory)
def generate_category_slug(sender, instance, **kwargs):
    """Genereer slug voor categorie als deze niet bestaat"""
    if not instance.slug:
        instance.slug = slugify(instance.name)
        
        # Zorg voor unieke slug
        counter = 1
        original_slug = instance.slug
        while ServiceCategory.objects.filter(slug=instance.slug).exists():
            instance.slug = f"{original_slug}-{counter}"
            counter += 1