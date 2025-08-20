# all
import jwt
import random

from django.conf import settings
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from jwt.exceptions import ExpiredSignatureError
from rest_framework_simplejwt.tokens import RefreshToken
# from django.db import transaction
from django.template.loader import render_to_string
from module.models import Modules
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# model
from .models import ProfilUser,UserToken

# model
from .serializers import CustomTokenObtainPairSerializer
from .serializers import ProfilUserSerializer
from solar_backend.utils import Util

def send_email_notification(email_content, email, titre):
    content = {
        "email_body": email_content,
        "to_email": email,
        "email_subject": titre,
    }
    Util.send_email(content)


@swagger_auto_schema(
    method='get',
    operation_description="Teste l'envoi d'email",
    responses={
        200: openapi.Response('Email envoyé avec succès'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
def teste_email(request):
   send_email_notification("salut",'brokewala@gmail.com',"teste salut")
   return Response({"message": "Email sent successfully"})


@swagger_auto_schema(
    method='post',
    operation_description="Décode un token JWT",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token JWT à décoder')
        }
    ),
    responses={
        200: openapi.Response('Token décodé avec succès'),
        400: openapi.Response('Token manquant'),
        401: openapi.Response('Token expiré ou invalide')
    }
)
@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def decode_token(request):
    # Check if the 'token' is provided in the request data
    if "token" not in request.data:
        return Response(
            {"error": "token does not exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Decode token using the SECRET_KEY from Django settings
        decoded_token = jwt.decode(
            request.data["token"], settings.SECRET_KEY, algorithms=["HS256"]
        )
        # Assuming the decoded token contains 'token_type' and 'user_id' keys
        token_type = decoded_token["token_type"]
        user_id = decoded_token["user_id"]

        # Return the decoded values
        return Response(
            {
                "token_type": token_type,
                "user_id": user_id,
            }
        )

    except jwt.exceptions.ExpiredSignatureError:
        return Response(
            {"error": "token has expired"}, status=status.HTTP_401_UNAUTHORIZED
        )

    except jwt.exceptions.InvalidTokenError:
        return Response({"error": "invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

    except jwt.exceptions.DecodeError:
        return Response(
            {"error": "error decoding token"}, status=status.HTTP_401_UNAUTHORIZED
        )


# user by token
@swagger_auto_schema(
    method='post',
    operation_description="Récupère un utilisateur par son token JWT",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token JWT de l\'utilisateur')
        }
    ),
    responses={
        200: ProfilUserSerializer,
        401: openapi.Response('Token expiré'),
        404: openapi.Response('Utilisateur non trouvé')
    }
)
@api_view(["POST"])
def user_by_token(request):
    # if is none
    if request.data.get("token") is None:
        return Response(
            {"error": "token does not exist"}, status=status.HTTP_404_NOT_FOUND
        )
    # decode token
    try:
        decoded_token = jwt.decode(
            request.data.get("token"), settings.SECRET_KEY, algorithms=["HS256"]
        )
    except ExpiredSignatureError:  # Capturer l'exception ExpiredSignatureError
        return Response(
            {"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED
        )
    except jwt.exceptions.DecodeError:
        return Response(
            {"error": "user does not exists"}, status=status.HTTP_404_NOT_FOUND
        )

    user_id = decoded_token["user_id"]

    # get user
    try:
        user = ProfilUser.objects.get(id=user_id)
    except ProfilUser.DoesNotExist:
        return Response(
            {"error": "user does not exists"}, status=status.HTTP_404_NOT_FOUND
        )

    # searilise 
    serializer = ProfilUserSerializer(user, many=False)
    return Response(serializer.data,status=status.HTTP_200_OK)


# refresh token view
class CustomTokenRefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")
        if access_token and refresh_token:
            # decode token
            decoded_token = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )

            # Assuming the decoded token contains 'token_type' and 'user_id' keys
            user_id = decoded_token["user_id"]

            # save token
            user_token_obj = UserToken.objects.filter(user__id=user_id).first()
            if user_token_obj:
                # If the user token exists, update its values
                user_token_obj.access_token = access_token
                user_token_obj.refresh_token = refresh_token
                user_token_obj.save()
            else:
                UserToken.objects.create(
                    user=user_token_obj,
                    access_token=access_token,
                    refresh_token=refresh_token,
                )
        # Récupérer les tokens générés par le super()
        response = super().finalize_response(request, response, *args, **kwargs)
        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        # Récupérer les tokens générés par le super()
        response = super().finalize_response(request, response, *args, **kwargs)
        return response


# create_admin_of_user
@swagger_auto_schema(
    method='post',
    operation_description="Crée un utilisateur administrateur",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password', 'first_name', 'last_name'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Adresse email unique'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Mot de passe'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Prénom'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nom de famille')
        }
    ),
    responses={
        201: ProfilUserSerializer,
        400: openapi.Response('Email déjà existant ou données manquantes'),
        500: 'Internal Server Error'
    }
)
@api_view(["POST"])
def create_admin_of_user(request):
    email = request.data.get("email")
    if ProfilUser.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    if (
        request.data.get("email") is None
        or request.data.get("password") is None
        or request.data.get("first_name") is None
        or request.data.get("last_name") is None
    ):
        return Response(
            {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
        )

    # create user
    user = ProfilUser.objects.create_superuser(
        email=request.data["email"],
        password=request.data["password"],
        first_name=request.data["first_name"],
        last_name=request.data["last_name"],
        role="admin",
    )
    # save into database
    user.save()
    serializer = ProfilUserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les administrateurs",
    responses={
        200: ProfilUserSerializer(many=True),
        404: openapi.Response('Aucun administrateur trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_admin(request):
    try:
        # Récupérer l'utilisateur depuis la base de données avec only
        user = ProfilUser.objects.filter(is_superuser=True)
    except ProfilUser.DoesNotExist:
        return Response({"error": "Users not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProfilUserSerializer(user, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les clients",
    responses={
        200: ProfilUserSerializer(many=True),
        404: openapi.Response('Aucun client trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_customers(request):
    try:
        # Récupérer l'utilisateur depuis la base de données avec only
        user = ProfilUser.objects.filter(role="customer").order_by("-createdAt")
    except ProfilUser.DoesNotExist:
        return Response({"error": "Users not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProfilUserSerializer(user, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ProfilUser
class ProfilUserModelViewSet(viewsets.ModelViewSet):
    queryset = ProfilUser.objects.all()
    serializer_class = ProfilUserSerializer
    # permission_classes = [IsAuthenticated]



# users
class UsersAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Crée un nouvel utilisateur client",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Adresse email unique'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Mot de passe'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Prénom'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nom de famille'),
                'code_postal': openapi.Schema(type=openapi.TYPE_STRING, description='Code postal'),
                'adresse': openapi.Schema(type=openapi.TYPE_STRING, description='Adresse'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Numéro de téléphone')
            }
        ),
        responses={
            201: ProfilUserSerializer,
            400: openapi.Response('Email déjà existant ou données manquantes'),
            500: 'Internal Server Error'
        }
    )
    def post(self, request): 
        email = request.data.get("email")
        if ProfilUser.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        if (
            request.data.get("email") is None
            or request.data.get("password") is None
            or request.data.get("first_name") is None
            or request.data.get("last_name") is None
        ):
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        # create user
        user = ProfilUser.objects.create_user(
            email=request.data["email"],
            password=request.data["password"],
            first_name=request.data["first_name"],
            last_name=request.data["last_name"],
            role="customer",
        )
        if request.data.get("code_postal"):
            user.code_postal =request.data.get("code_postal")
        
        if request.data.get("adresse"):
            user.adresse =request.data.get("adresse")
        
        if request.data.get("phone"):
            user.phone =request.data.get("phone")
        
        # save into database
        user.save()
            
        serializer = ProfilUserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
# signup with code
@swagger_auto_schema(
    method='post',
    operation_description="Inscription d'un utilisateur avec envoi de code de vérification par email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password', 'first_name', 'last_name'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Adresse email unique'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Mot de passe'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Prénom'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nom de famille'),
            'code_postal': openapi.Schema(type=openapi.TYPE_STRING, description='Code postal'),
            'adresse': openapi.Schema(type=openapi.TYPE_STRING, description='Adresse'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Numéro de téléphone')
        }
    ),
    responses={
        201: ProfilUserSerializer,
        400: openapi.Response('Email déjà existant ou données manquantes'),
        500: 'Internal Server Error'
    }
)
@api_view(["POST"])
def signup_user_with_code_in_email(request):
    email = request.data.get("email")
    if ProfilUser.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    if (
        request.data.get("email") is None
        or request.data.get("password") is None
        or request.data.get("first_name") is None
        or request.data.get("last_name") is None
    ):
        return Response(
            {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
        )

    # create user
    user = ProfilUser.objects.create_user(
        email=request.data["email"],
        password=request.data["password"],
        first_name=request.data["first_name"],
        last_name=request.data["last_name"],
        role="customer",
    )
    if request.data.get("code_postal"):
        user.code_postal =request.data.get("code_postal")
    
    if request.data.get("adresse"):
        user.adresse =request.data.get("adresse")
    
    if request.data.get("phone"):
        user.phone =request.data.get("phone")
    
    # save into database
    user.save()
    # redis
    otp = random.randint(100000, 900000)
    user.code = otp
    user.save()
    # send email
    subject = f"Solar | Code of verification"
    html_message = render_to_string(
        "code.html",
        {"otp": otp, "email": email},
    )
    # send
    send_email_notification(html_message, email, subject)

    
    serializer = ProfilUserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# get code of user with user id
@swagger_auto_schema(
    method='get',
    operation_description="Récupère le code de vérification d'un utilisateur par son ID",
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_PATH,
            description="Identifiant unique de l'utilisateur",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: ProfilUserSerializer,
        404: openapi.Response('Utilisateur non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
def get_user_code_with_user_id(request, user_id):
    try:
        user = ProfilUser.objects.only(
            "id", "email", "code", "first_name"
        ).get(id=user_id)
    except ProfilUser.DoesNotExist:
        return Response(
            {"error": "user does not exists"}, status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProfilUserSerializer(user, many=False)
    return Response(serializer.data)


# post code of confirmation
@swagger_auto_schema(
    method='post',
    operation_description="Vérifie le code de confirmation d'un utilisateur",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['code', 'user_id'],
        properties={
            'code': openapi.Schema(type=openapi.TYPE_STRING, description='Code de vérification'),
            'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID de l\'utilisateur')
        }
    ),
    responses={
        201: openapi.Response('Code vérifié avec succès, tokens générés'),
        400: openapi.Response('Code incorrect'),
        404: openapi.Response('Utilisateur non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["POST"])
def verify_code_of_user(request):
    code = request.data.get("code")
    user_id = request.data.get("user_id")

    try:
        user = ProfilUser.objects.get(id=user_id)
    except ProfilUser.DoesNotExist:
        return Response(
            {"error": "user does not exists"}, status=status.HTTP_404_NOT_FOUND
        )
    # verify code of user
    if code == user.code:
        user.status = True
        user.is_verified = True
        user.save()
        
        # Création du module si non existant
        Modules.objects.get_or_create(user=user)
     
        # Envoi de la réponse
        refresh = RefreshToken.for_user(user)
        response_data = {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user_id": user.id,
            "email": user.email,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    else:
        return Response(
            {"error": "your code of confirmation not correct"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@swagger_auto_schema(
    method='post',
    operation_description="Renvoye le code de vérification par email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='ID de l\'utilisateur')
        }
    ),
    responses={
        200: openapi.Response('Code renvoyé avec succès'),
        404: openapi.Response('Utilisateur non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["POST"])
# resend code of user
def resend_code_of_signup(request):
    user_id = request.data.get("user_id")
    try:
        user = ProfilUser.objects.get(id=user_id)
    except ProfilUser.DoesNotExist:
        return Response(
            {"error": "user does not exists"}, status=status.HTTP_404_NOT_FOUND
        )
    otp = random.randint(100000, 900000)
    user.code = otp
    user.save()
    # send email
    # send email
    subject = f"Solar | Code of verification"
    html_message = render_to_string(
        "code.html",
        {"otp": otp, "email": user.email},
    )
    # send
    send_email_notification(html_message, user.email, subject)
    # return data
    response_data = {
        "user_id": user.id,
        "email": user.email,
        "code": user.code,
    }
    return Response(response_data)


# update user profile
@swagger_auto_schema(
    method='put',
    operation_description="Met à jour le profil utilisateur avec authentification par token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token', 'first_name', 'last_name', 'email'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token JWT de l\'utilisateur'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Prénom'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nom de famille'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Adresse email'),
            'adresse': openapi.Schema(type=openapi.TYPE_STRING, description='Adresse'),
            'code_postal': openapi.Schema(type=openapi.TYPE_STRING, description='Code postal'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Numéro de téléphone')
        }
    ),
    responses={
        200: ProfilUserSerializer,
        400: openapi.Response('Token manquant ou email déjà existant'),
        401: openapi.Response('Token expiré ou invalide'),
        404: openapi.Response('Utilisateur non trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["PUT"])
def update_user_profile(request):
    """
    Met à jour le profil utilisateur avec authentification par token
    """
    token = request.data.get("token")
    if not token:
        return Response(
            {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    # decode token
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return Response(
            {"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED
        )
    except jwt.InvalidTokenError:
        return Response(
            {"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED
        )

    user_id = decoded_token["user_id"]

    # get user
    try:
        user = ProfilUser.objects.get(id=user_id)
    except ProfilUser.DoesNotExist:
        return Response(
            {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
        )

    # Validation des champs requis
    if not request.data.get("first_name") or not request.data.get("last_name") or not request.data.get("email"):
        return Response(
            {"error": "First name, last name and email are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Vérifier si l'email existe déjà pour un autre utilisateur
    email = request.data.get("email")
    if ProfilUser.objects.filter(email=email).exclude(id=user_id).exists():
        return Response(
            {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Mettre à jour les champs
    user.first_name = request.data.get("first_name")
    user.last_name = request.data.get("last_name")
    user.email = email

    if request.data.get("adresse"):
        user.adresse = request.data.get("adresse")

    if request.data.get("code_postal"):
        user.code_postal = request.data.get("code_postal")

    if request.data.get("phone"):
        user.phone = request.data.get("phone")

    # Sauvegarder
    user.save()

    # Retourner les données mises à jour
    serializer = ProfilUserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK) 