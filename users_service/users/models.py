from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField


def user_profile_pic_path(instance, filename):
    # Enregistre les photos dans : media/profiles/user_<id>/<filename>
    return f'profiles/user_{instance.id}/{filename}'


class CustomUser(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrateur'),
        ('CHEF_DE_PROJET', 'Chef de Projet'),
        ('DEVELOPPEUR', 'Développeur'),
        ('TESTEUR', 'Testeur'),
    )

    nom = models.CharField(max_length=255, verbose_name="Nom complet", default='Utilisateur inconnu') 
    email = models.EmailField(unique=True, verbose_name="Adresse e-mail")
    role = models.CharField(max_length=50, choices=ROLES, default='DEVELOPPEUR', verbose_name="Rôle")
    annees_experience = models.IntegerField(default=0, verbose_name="Années d'expérience")
    charge_travail = models.FloatField(default=0.0, verbose_name="Charge de travail (heures)")
    competences = JSONField(default=list, verbose_name="Compétences")  # Stocke une liste JSON, ex. ["Python", "JavaScript"]
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    profile_picture = models.ImageField(
        upload_to=user_profile_pic_path,
        null=True,
        blank=True,
        verbose_name="Photo de profil"
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nom']

    class Meta:
        verbose_name = 'Collaborateur'
        verbose_name_plural = 'Collaborateurs'

    def save(self, *args, **kwargs):
        # Supprime l'ancienne image si elle existe lors de la mise à jour
        try:
            old = CustomUser.objects.get(id=self.id)
            if old.profile_picture and old.profile_picture != self.profile_picture:
                old.profile_picture.delete(save=False)
        except CustomUser.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.get_role_display()})"



# from django.contrib.auth.models import AbstractUser
# from django.db import models


# def user_profile_pic_path(instance, filename):
#     # Enregistre les photos dans : media/profiles/user_<id>/<filename>
#     return f'profiles/user_{instance.id}/{filename}'

# class CustomUser(AbstractUser):
#     ROLES = (
#         ('ADMIN', 'Administrateur'),
#         ('USER', 'Utilisateur standard'),
#     )
    
#     role = models.CharField(max_length=50, choices=ROLES, default='USER')
#     email = models.EmailField(unique=True) 
#     date_joined = models.DateTimeField(auto_now_add=True)
#     profile_picture = models.ImageField(upload_to=user_profile_pic_path,
#         null=True,
#         blank=True,
#         default='profiles/default.png')


#     USERNAME_FIELD = 'username'  
#     REQUIRED_FIELDS = ['email']  

#     class Meta:
#         verbose_name = 'User'
#         verbose_name_plural = 'Users'



#     def save(self, *args, **kwargs):
#         # Supprime l'ancienne image si elle existe lors de la mise à jour
#         try:
#             old = CustomUser.objects.get(id=self.id)
#             if old.profile_picture and old.profile_picture != self.profile_picture:
#                 old.profile_picture.delete(save=False)
#         except CustomUser.DoesNotExist:
#             pass
#         super().save(*args, **kwargs)


#     def __str__(self):
#         return f"{self.email} ({self.role})"