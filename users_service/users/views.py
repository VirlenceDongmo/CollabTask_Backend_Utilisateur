
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import generics, permissions, status
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
import logging
from django.conf import settings
import requests
from .models import CustomUser
from .serializers import  ChangePasswordSerializer, CustomTokenObtainPairSerializer, CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
import logging
from django.contrib.auth.models import Group
from django.contrib.auth import update_session_auth_hash
from .producteurs import NotificationProducer



@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

User = get_user_model()

# class CurrentUserView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         return Response({
#             'id': request.user.id,
#             'username': request.user.username,
#             'email': request.user.email,
#             'role': request.user.role
#         })


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    


class UserRoleView(APIView):
    
    def get(self, request, role):
        try:
            user = User.objects.get(role=role)
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'annees_experience':user.annees_experience,
                'charge_travail': user.charge_travail,
                'competence':user.competences,
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)



class UserDetailView(APIView):
    permission_classes = [permissions.AllowAny] 
    
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            return Response({
                'id': user.id,
                'username': user.nom,
                'email': user.email,
                'role': user.role,
                'annees_experience':user.annees_experience,
                'charge_travail': user.charge_travail,
                'competence':user.competences,
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


logger = logging.getLogger(__name__)

class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def perform_create(self, serializer):
        try:
            user = serializer.save()
            self._send_welcome_email(user)
            return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur: {str(e)}")
            return Response({"detail": f"Erreur lors de la création: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_welcome_email(self, user):
        notification_data = {
            'event_type': 'compte créé',
            'contenu': self._get_welcome_email_content(user),
            'destinataire': user.id,
            'destinateur': self.request.user.id if self.request.user else None,
            'tache': None,
            'subject': f"Votre compte sur {settings.PLATFORM_NAME}",
            'recipient': user.email,
        }

        try:
            print(f"Tentative d'envoi à RabbitMQ pour {user.email}")
            producer = NotificationProducer()
            if producer.send_notification(notification_data):
                print("Notification envoyée à RabbitMQ avec succès")
            else:
                print("Échec d'envoi à RabbitMQ, tentative de fallback...")
                self._send_fallback_email(notification_data)
        except Exception as e:
            logger.error(f"Erreur RabbitMQ: {str(e)}")
            # Envoi direct en fallback
            self._send_fallback_email(notification_data)

    def _send_fallback_email(self, notification_data):
        """Envoyer un email en cas d'échec de RabbitMQ"""
        try:
            send_mail(
                subject=notification_data['subject'],
                message=notification_data['contenu'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification_data['recipient']],
                fail_silently=False
            )
            print(f"Email de fallback envoyé à {notification_data['recipient']}")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de fallback: {str(e)}")

    def _get_welcome_email_content(self, user):
        return f"""
        Bonjour {user.nom},

        Votre compte sur {settings.PLATFORM_NAME} a été créé avec succès.

        Identifiants de connexion:
        - Nom d'utilisateur: {user.nom}
        - Mot de passe temporaire: CollabTask000000

        Pour votre sécurité, nous vous recommandons de:
        1. Vous connecter immédiatement à : {settings.PLATFORM_URL}
        2. Changer votre mot de passe

        Support technique: {settings.SUPPORT_EMAIL} | {settings.SUPPORT_PHONE}

        Cordialement,
        L'équipe {settings.PLATFORM_NAME}
        """



# logger = logging.getLogger(__name__)


# class CreateUserView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = CustomUserSerializer

#     def perform_create(self, serializer):
#         try:
#             user = serializer.save()
#             self._send_welcome_email(user)
#             return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             logger.error(f"Erreur lors de la création de l'utilisateur: {str(e)}")
#             return Response({"detail": f"Erreur lors de la création: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def _send_welcome_email(self, user):
#         notification_data = {
#             'event_type': 'compte créé',
#             'recipient': user.email,
#             'subject': f"Votre compte sur {settings.PLATFORM_NAME}",
#             'body': self._get_welcome_email_content(user),
#             'user_id': user.id,
#             'admin_id': self.request.user.id if self.request.user else None
#         }

#         try:
#             print(f"Tentative d'envoi à RabbitMQ pour {user.email}")
#             producer = NotificationProducer()
#             if producer.send_notification(notification_data):
#                 print("Notification envoyée à RabbitMQ avec succès")
#             else:
#                 print("Échec d'envoi à RabbitMQ, tentative de fallback...")
#         except Exception as e:
#             logger.error(f"Erreur RabbitMQ: {str(e)}")
#             # Envoi direct en fallback
#             send_mail(
#                 subject=notification_data['subject'],
#                 message=notification_data['body'],
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False
#             )

#     def _get_welcome_email_content(self, user):
#         return f"""
#         Bonjour {user.nom},

#         Votre compte sur {settings.PLATFORM_NAME} a été créé avec succès.

#         Identifiants de connexion:
#         - Nom d'utilisateur: {user.nom}
#         - Mot de passe temporaire: CollabTask000000

#         Pour votre sécurité, nous vous recommandons de:
#         1. Vous connecter immédiatement à : {settings.PLATFORM_URL}
#         2. Changer votre mot de passe

#         Support technique: {settings.SUPPORT_EMAIL} | {settings.SUPPORT_PHONE}

#         Cordialement,
#         L'équipe {settings.PLATFORM_NAME}
#         """



class UpdateUserView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'id'  

    def patch(self, request, *args, **kwargs):
        user = self.get_object()  
        
        if 'current_password' in request.data:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)
                return Response({"detail": "Mot de passe mis à jour avec succès"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Pour les autres mises à jour
        return super().patch(request, *args, **kwargs)


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    



# views.py
class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}



class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        current_user = self.request.user
        is_regular_user = getattr(current_user, 'role', None) == 'USER'

        if is_regular_user:
            raise PermissionDenied("Seuls les administrateurs peuvent supprimer des utilisateurs.")

        try:
            print(f"Tentative de suppression de l'utilisateur {instance.id}")

            user_data = {
                'id': str(instance.id),
                'username': instance.username,
                'email': instance.email,
                'deleted_by': str(current_user.id) if current_user.id else None,
                'deleted_by_name': current_user.username if current_user.username else 'Unknown',
            }

            admin_emails = self._get_admin_emails()

            recipients = [email for email in admin_emails if email and email != instance.email]
            user_data['recipients'] = recipients

            instance.delete()
            print(f"Utilisateur {instance.id} supprimé avec succès")

            self._send_deletion_notification(user_data)

        except Exception as e:
            print(f"ERREUR CRITIQUE lors de la suppression de l'utilisateur {instance.id}: {str(e)}")
            raise ValidationError(f"Erreur lors de la suppression de l'utilisateur: {str(e)}")

    def _get_admin_emails(self):
        try:
            response = requests.get(
                f'{settings.USER_SERVICE_URL}/api/user/list/',
                headers={
                    'Authorization': self.request.headers.get('Authorization'),
                    'Content-Type': 'application/json',
                },
                timeout=2,
            )
            response.raise_for_status()
            users = response.json()
            return [user['email'] for user in users if user.get('role') == 'ADMIN' and user.get('email')]
        except Exception as e:
            print(f"Failed to get admin emails: {e}")
            return []

    def _send_deletion_notification(self, user_data):
        try:
            print(f"Préparation notification suppression: {user_data}")
            producer = NotificationProducer()
            notification_data = {
                'event_type': 'utilisateur supprimé',
                'user_id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'deleted_by': user_data['deleted_by'],
                'deleted_by_name': user_data['deleted_by_name'],
                'recipients': user_data['recipients'],
                'priority': 'high',
            }
            producer.send_notification(notification_data)
            print("Notification de suppression envoyée")
        except Exception as e:
            print(f"Erreur envoi notification suppression: {str(e)}")





