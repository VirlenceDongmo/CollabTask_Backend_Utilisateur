from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import CustomUser
import re

class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'nom', 'email', 'role', 'annees_experience', 'charge_travail',
        'display_competences', 'display_profile_picture', 'is_staff', 'is_active', 'date_joined'
    )
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'nom', 'email', 'competences')
    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('username', 'nom', 'email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('role', 'annees_experience', 'charge_travail', 'competences', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')
        }),
        ('Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nom', 'email', 'password1', 'password2', 'role', 'annees_experience', 'charge_travail', 'competences', 'profile_picture', 'is_staff', 'is_active'),
        }),
    )

    readonly_fields = ('username', 'date_joined', 'last_login')

    def save_model(self, request, obj, form, change):
        """
        Générer un username unique à partir de nom lors de la création.
        """
        if not change:  # Création d'un nouvel utilisateur
            nom = form.cleaned_data.get('nom', '')
            base_username = re.sub(r'[^a-zA-Z0-9]', '', nom.lower().replace(' ', '')) or form.cleaned_data.get('email', '').split('@')[0]
            username = base_username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            obj.username = username
        super().save_model(request, obj, form, change)

    def display_competences(self, obj):
        """
        Afficher les compétences sous forme de chaîne lisible.
        """
        if obj.competences:
            return ", ".join(obj.competences)
        return "-"
    display_competences.short_description = 'Compétences'

    def display_profile_picture(self, obj):
        """
        Afficher une miniature de la photo de profil.
        """
        if obj.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />', obj.profile_picture.url)
        return "-"
    display_profile_picture.short_description = 'Photo de profil'

admin.site.register(CustomUser, CustomUserAdmin)