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

# model
from .models import ProfilUser,UserToken

# model
from .serializers import CustomTokenObtainPairSerializer
from .serializers import ProfilUserSerializer
from solar_backend.utils import Util
from module.views import create_module

def send_email_notification(email_content, email, titre):
    content = {
        "email_body": email_content,
        "to_email": email,
        "email_subject": titre,
    }
    Util.send_email(content)


@api_view(["GET"])
def teste_email(request):
   send_email_notification("salut",'brokewala@gmail.com',"teste salut")
   return Response({"message": "Email sent successfully"})


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
@api_view(["GET"])
def get_user_code_with_user_id(request, user_id):
    try:
        user = ProfilUser.objects.only(
            "id", "email", "code", "username", "first_name"
        ).get(id=user_id)
    except ProfilUser.DoesNotExist:
        return Response(
            {"error": "user does not exists"}, status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProfilUserSerializer(user, many=False)
    return Response(serializer.data)


# post code of confirmation
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
        user.save()
        
        # create module
        create_module(user.id,user.first_name,user.last_name)

     
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

