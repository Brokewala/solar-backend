# all
import jwt
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

# from rest_framework_simplejwt.tokens import RefreshToken
# from django.db import transaction

# model
from .models import ProfilUser,UserToken

# model
from .serializers import CustomTokenObtainPairSerializer
from .serializers import ProfilUserSerializer


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

    
    