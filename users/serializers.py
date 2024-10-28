from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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


class UserTokenSerializer(ModelSerializer):
    user = ProfilUserSerializer()

    class Meta:
        model = UserToken
        fields = "__all__"


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
            raise serializers.ValidationError("Invalid credentials")

        if isinstance(user, ProfilUser):
            refresh = self.get_token(user)

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


