from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import ContactMessage, NewsletterSubscriber


@receiver(post_save, sender=ContactMessage)
def send_notifications_on_contact_message(sender, instance, created, **kwargs):
    """
    Stuur notificaties bij aanmaak of update van contactberichten.
    
    TECHNISCHE CONCEPTEN:
    - Post-save signal handling
    - Email notifications
    - Conditional logic
    """
    
    if created:
        # Stuur bevestiging naar verzender
        send_contact_confirmation(instance)
        
        # Stuur notificatie naar admin
        send_admin_notification(instance)
    
    elif instance.status in ['resolved', 'closed'] and not instance.responded_at:
        # Update responded_at bij afhandeling
        instance.responded_at = timezone.now()
        instance.save(update_fields=['responded_at'])
        
        # Stuur afhandelingsmail naar verzender
        send_resolution_notification(instance)


@receiver(pre_save, sender=ContactMessage)
def log_status_changes(sender, instance, **kwargs):
    """
    Log status wijzigingen voor audit trail.
    
    TECHNISCHE CONCEPTEN:
    - Pre-save signal voor change detection
    - Field change tracking
    - Audit logging
    """
    
    if instance.pk:
        try:
            old_instance = ContactMessage.objects.get(pk=instance.pk)
            
            # Controleer status wijziging
            if old_instance.status != instance.status:
                # Log status wijziging
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
                note = f"[{timestamp} System]: Status changed from {old_instance.status} to {instance.status}"
                
                # Voeg toe aan bestaande notities
                instance.response_notes = f"{note}\n{instance.response_notes or ''}"
        
        except ContactMessage.DoesNotExist:
            pass


@receiver(post_save, sender=NewsletterSubscriber)
def send_confirmation_email(sender, instance, created, **kwargs):
    """
    Stuur bevestigingsmail bij nieuwsbrief inschrijving.
    
    TECHNISCHE CONCEPTEN:
    - Double opt-in flow
    - Email template rendering
    - Token-based confirmation
    """
    
    if created:
        send_subscription_confirmation(instance)


# Helper functies voor email sending
def send_contact_confirmation(message):
    """Stuur bevestigingsmail naar verzender"""
    try:
        subject = _('Bevestiging van je contactverzoek')
        
        context = {
            'message': message,
            'site_name': getattr(settings, 'SITE_NAME', 'Onze Website'),
        }
        
        text_message = render_to_string('emails/contact_confirmation.txt', context)
        html_message = render_to_string('emails/contact_confirmation.html', context)
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.email],
            html_message=html_message,
            fail_silently=True
        )
    
    except Exception as e:
        # Log error maar crash niet
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send contact confirmation: {e}")


def send_admin_notification(message):
    """Stuur notificatie naar admin"""
    try:
        # Bepaal ontvanger
        recipient = message.category.email_recipient or settings.ADMIN_EMAIL
        
        subject = _('Nieuw contactbericht ontvangen: {}').format(message.reference_number)
        
        context = {
            'message': message,
            'admin_url': f"{settings.SITE_URL}/admin/contact/contactmessage/{message.id}/change/",
        }
        
        text_message = render_to_string('emails/admin_notification.txt', context)
        html_message = render_to_string('emails/admin_notification.html', context)
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=True
        )
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send admin notification: {e}")


def send_resolution_notification(message):
    """Stuur afhandelingsmail naar verzender"""
    try:
        subject = _('Update over je contactverzoek')
        
        context = {
            'message': message,
            'site_name': getattr(settings, 'SITE_NAME', 'Onze Website'),
        }
        
        text_message = render_to_string('emails/resolution_notification.txt', context)
        html_message = render_to_string('emails/resolution_notification.html', context)
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.email],
            html_message=html_message,
            fail_silently=True
        )
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send resolution notification: {e}")


def send_subscription_confirmation(subscriber):
    """Stuur bevestigingsmail voor nieuwsbrief"""
    try:
        subject = _('Bevestig je nieuwsbrief inschrijving')
        
        context = {
            'subscriber': subscriber,
            'confirmation_url': f"{settings.SITE_URL}/api/v1/contact/newsletter/confirm/{subscriber.subscription_token}/",
            'site_name': getattr(settings, 'SITE_NAME', 'Onze Website'),
        }
        
        text_message = render_to_string('emails/newsletter_confirmation.txt', context)
        html_message = render_to_string('emails/newsletter_confirmation.html', context)
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=True
        )
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send subscription confirmation: {e}")