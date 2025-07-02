from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from .models import CustomUser
import re


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = self.context['request'].user
        
        if not check_password(data['current_password'], user.password):
            raise serializers.ValidationError({"current_password": "Le mot de passe actuel est incorrect"})
        
        password_validation.validate_password(data['new_password'], user)
        
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['id'] = user.id
        token['username'] = user.username
        token['nom'] = user.nom
        token['email'] = user.email
        token['role'] = user.role
        token['annees_experience'] = user.annees_experience
        token['charge_travail'] = user.charge_travail
        token['competences'] = user.competences
        return token


class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'nom', 'email', 'password', 'password2', 'role',
            'annees_experience', 'charge_travail', 'competences', 'profile_picture', 'date_joined'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
            'profile_picture': {'required': False},
            'date_joined': {'read_only': True},
            'last_login': {'read_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})

        if data.get('annees_experience', 0) < 0:
            raise serializers.ValidationError({"annees_experience": "Les années d'expérience ne peuvent pas être négatives."})

        charge_travail = data.get('charge_travail', 0.0)
        if charge_travail < 0 or charge_travail > 100:
            raise serializers.ValidationError({"charge_travail": "La charge de travail doit être entre 0 et 100."})

        password_validation.validate_password(data['password'], self.instance)

        return data

    def create(self, validated_data):
        # Supprimer password2
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        # Générer un username unique basé sur nom ou email
        nom = validated_data.get('nom', '')
        email = validated_data.get('email', '')
        base_username = re.sub(r'[^a-zA-Z0-9]', '', nom.lower().replace(' ', '')) or email.split('@')[0]
        username = base_username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        validated_data['username'] = username
        
        # Gestion du fichier de profil
        profile_picture = validated_data.pop('profile_picture', None)
        
        # Créer l'utilisateur
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        
        if profile_picture:
            user.profile_picture = profile_picture
        
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        profile_picture = validated_data.pop('profile_picture', None)
        if profile_picture:
            instance.profile_picture = profile_picture
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture.url)
        return None




# from rest_framework import serializers
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, password_validation
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework_simplejwt.views import TokenObtainPairView
# from django.contrib.auth import get_user_model
# from .models import CustomUser
# from django.contrib.auth.hashers import check_password



# User = get_user_model()



# class ChangePasswordSerializer(serializers.Serializer):
#     current_password = serializers.CharField(required=True, write_only=True)
#     new_password = serializers.CharField(required=True, write_only=True)

#     def validate(self, data):
#         user = self.context['request'].user
        
#         # Vérifie l'ancien mot de passe
#         if not check_password(data['current_password'], user.password):
#             raise serializers.ValidationError({"current_password": "Le mot de passe actuel est incorrect"})
        
#         # Valide le nouveau mot de passe
#         password_validation.validate_password(data['new_password'], user)
        
#         return data




# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Ajoutez des claims personnalisés
#         token['id'] = user.id
#         token['username'] = user.username
#         token['email'] = user.email
#         token['role'] = user.role
        

#         return token


# class CustomUserSerializer(serializers.ModelSerializer):
#     profile_picture = serializers.SerializerMethodField()  
#     password2 = serializers.CharField(write_only=True)

#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'password', 'password2', 'role', 
#                  'profile_picture']  
#         extra_kwargs = {
#             'password': {'write_only': True},
#             'profile_picture': {'required': False, 'write_only': True},
#             'date_joined': {'read_only': True},
#             'last_login': {'read_only': True},
#         }

#     def validate(self, data):
#         if data['password'] != data['password2']:
#             raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password2')
#         password = validated_data.pop('password')
        
#         # Gestion du fichier de profil
#         profile_picture = validated_data.pop('profile_picture', None)
#         user = CustomUser.objects.create_user(**validated_data)
#         user.set_password(password)
        
#         if profile_picture:
#             user.profile_picture = profile_picture
        
#         user.is_active = True
#         user.save()
#         return user

#     def get_profile_picture(self, obj):
#         if obj.profile_picture:
#             return self.context['request'].build_absolute_uri(obj.profile_picture.url)
#         return None

   