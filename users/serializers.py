from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

# model
from .models import ProfilUser,UserToken


# user profil serializer
class ProfilUserSerializer(ModelSerializer):

    class Meta:
        model = ProfilUser
        exclude = (
            "password",
            "groups",
            "user_permissions",
        )
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique de l\'utilisateur'},
            'first_name': {'help_text': 'Prénom de l\'utilisateur'},
            'last_name': {'help_text': 'Nom de famille de l\'utilisateur'},
            'email': {'help_text': 'Adresse email unique de l\'utilisateur'},
            'role': {'help_text': 'Rôle de l\'utilisateur dans le système'},
            'phone': {'help_text': 'Numéro de téléphone de l\'utilisateur'},
            'adresse': {'help_text': 'Adresse physique de l\'utilisateur'},
            'code_postal': {'help_text': 'Code postal de l\'utilisateur'},
            'code': {'help_text': 'Code d\'identification de l\'utilisateur'},
            'status': {'help_text': 'Statut actif/inactif de l\'utilisateur'},
            'is_staff': {'help_text': 'Indique si l\'utilisateur est membre du staff'},
            'is_superuser': {'help_text': 'Indique si l\'utilisateur est super utilisateur'},
            'image': {'help_text': 'Photo de profil de l\'utilisateur'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création du compte'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


class UserTokenSerializer(ModelSerializer):
    user = ProfilUserSerializer()

    class Meta:
        model = UserToken
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True, 'help_text': 'Identifiant unique du token'},
            'user': {'help_text': 'Utilisateur associé à ce token'},
            'access_token': {'help_text': 'Token d\'accès JWT'},
            'refresh_token': {'help_text': 'Token de rafraîchissement JWT'},
            'createdAt': {'read_only': True, 'help_text': 'Date de création du token'},
            'updatedAt': {'read_only': True, 'help_text': 'Date de dernière modification'}
        }


# token customise
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        print("validating",attrs)
        credentials = {"email": "", "password": attrs.get("password")}

        if "@" in attrs.get("email"):
            credentials["email"] = attrs.get("email")
        else:
            credentials["username"] = attrs.get("username")

        user = authenticate(**credentials)

        if user is None:
            raise serializers.ValidationError("L\’adresse e-mail ou le mot de passe est incorrect.")
        

        if isinstance(user, ProfilUser):
            refresh = self.get_token(user)
            # verification of user 
            if not user.status or not user.is_verified:
                raise AuthenticationFailed({"detail": f"Votre compte est désactivé .", "user_id": user.id})
       
            # les token
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            # save token
            user_token_obj = UserToken.objects.filter(user=user).first()
            if user_token_obj:
                # If the user token exists, update its values
                user_token_obj.access_token = access_token
                user_token_obj.refresh_token = refresh_token
                user_token_obj.save()
            else:
                user_token_obj = UserToken.objects.create(
                    user=user,
                    access_token=access_token,
                    refresh_token=refresh_token,
                )

            # data
            data = {
                "refresh": refresh_token,
                "access": access_token,
                "user_id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "role": user.role,
            }
            return data

        else:
            raise serializers.ValidationError("User model not supported.")


