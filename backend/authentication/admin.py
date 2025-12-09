from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import CustomUser, UserProfile, UserActivityLog


class UserProfileInline(admin.StackedInline):
    """
    Inline admin voor UserProfile.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('profiel informatie')
    fieldsets = (
        (_('Contact informatie'), {
            'fields': ('secondary_email', 'secondary_phone')
        }),
        (_('Adres informatie'), {
            'fields': ('street', 'postal_code', 'city', 'country')
        }),
        (_('Persoonlijke informatie'), {
            'fields': ('date_of_birth', 'gender')
        }),
        (_('Social media'), {
            'fields': ('linkedin_url', 'twitter_handle')
        }),
        (_('Werk informatie'), {
            'fields': ('employee_id', 'hire_date')
        }),
        (_('Voorkeuren'), {
            'fields': ('theme', 'notification_preferences')
        }),
    )


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface voor CustomUser.
    """
    list_display = [
        'email', 'first_name', 'last_name', 'is_staff', 
        'is_active', 'date_joined', 'last_login_display'
    ]
    
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 
        'date_joined', 'last_login', 'department'
    ]
    
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    
    ordering = ['email']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Persoonlijke informatie'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')
        }),
        (_('Werk informatie'), {
            'fields': ('job_title', 'department')
        }),
        (_('Voorkeuren'), {
            'fields': ('language', 'timezone', 'email_notifications')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        (_('Datums'), {
            'fields': ('date_joined', 'last_login')
        }),
        (_('Notities'), {
            'fields': ('notes',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    inlines = [UserProfileInline]
    
    def last_login_display(self, obj):
        """Formatteer laatste login tijd"""
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return _('Nooit')
    last_login_display.short_description = _('Laatste login')


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    """
    Admin interface voor activiteitenlogs.
    """
    list_display = ['user_email', 'action', 'status_badge', 'ip_address', 'timestamp']
    list_filter = ['status', 'action', 'timestamp']
    search_fields = ['user__email', 'action', 'ip_address']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'details', 'status', 'timestamp']
    
    def user_email(self, obj):
        """Display gebruiker e-mail"""
        return obj.user.email if obj.user else _('Anonymous')
    user_email.short_description = _('Gebruiker')
    
    def status_badge(self, obj):
        """Display status met kleurcodering"""
        colors = {
            'success': 'green',
            'failed': 'red',
            'warning': 'orange'
        }
        
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = _('Status')