from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product, ProductReview
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Product)
def generate_product_slug(sender, instance, **kwargs):
    """Genereer slug als deze niet bestaat"""
    if not instance.slug:
        instance.slug = slugify(instance.title)
        
        # Zorg voor unieke slug
        counter = 1
        original_slug = instance.slug
        while Product.objects.filter(slug=instance.slug).exists():
            instance.slug = f"{original_slug}-{counter}"
            counter += 1


@receiver(post_save, sender=ProductReview)
def update_product_rating(sender, instance, created, **kwargs):
    """Update product rating wanneer een review wordt toegevoegd"""
    if instance.is_approved:
        product = instance.product
        
        # Bereken nieuwe gemiddelde rating
        approved_reviews = product.reviews.filter(is_approved=True)
        if approved_reviews.exists():
            total_rating = sum(review.rating for review in approved_reviews)
            avg_rating = total_rating / approved_reviews.count()
            
            # Hier kan je de avg_rating opslaan in het Product model
            # als je een cached veld wilt toevoegen
            logger.info(f"Product {product.id} heeft nu gemiddelde rating: {avg_rating}")