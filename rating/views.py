from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# models
from users.models import ProfilUser
from .models import Rating

# serializer
from .serializers import RatingSerializer


# get all Rating
@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les avis",
    responses={
        200: RatingSerializer(many=True),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_rating(request):
    ratings = Rating.objects.all().order_by("-createdAt")
    serializer = RatingSerializer(ratings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# get all module
@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les avis d'un utilisateur",
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
        200: RatingSerializer(many=True),
        404: openapi.Response('Aucun avis trouvé'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_rating_by_user(request, user_id):
    try:
        ratings = Rating.objects.filter(user__id=user_id).order_by("-createdAt")
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Rating.DoesNotExist:
        return Response(
            {"error": "No ratings found for this user"},
            status=status.HTTP_404_NOT_FOUND,
        )


# Rating APIView
class RatingAPIView(APIView):

    def get_object(self, rating_id):
        try:
            return Rating.objects.get(id=rating_id)
        except Rating.DoesNotExist:
            return Response(
                {"error": "rating not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Crée un nouvel avis",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['score', 'comment', 'user'],
            properties={
                'score': openapi.Schema(type=openapi.TYPE_STRING, description='Note de l\'avis'),
                'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Commentaire de l\'avis'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='ID de l\'utilisateur')
            }
        ),
        responses={
            201: RatingSerializer,
            400: openapi.Response('Données manquantes'),
            500: 'Internal Server Error'
        }
    )
    def post(self, request):
        score = request.data.get("score")
        comment = request.data.get("comment")
        user = request.data.get("user")
        if score is None or comment is None or user is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        #  user
        user_value = get_object_or_404(ProfilUser, id=user)

        # create rating
        rating = Rating.objects.create(
            score=score,
            comment=comment,
            user=user_value,
        )
        # save into database
        rating.save()

        serializer = RatingSerializer(rating, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Récupère un avis par son ID",
        manual_parameters=[
            openapi.Parameter(
                'rating_id',
                openapi.IN_PATH,
                description="Identifiant unique de l'avis",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: RatingSerializer,
            404: openapi.Response('Avis non trouvé'),
            500: 'Internal Server Error'
        }
    )
    def get(self, request, rating_id):
        rating = self.get_object(rating_id=rating_id)
        serializer = RatingSerializer(rating, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Met à jour un avis par son ID",
        manual_parameters=[
            openapi.Parameter(
                'rating_id',
                openapi.IN_PATH,
                description="Identifiant unique de l'avis",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'score': openapi.Schema(type=openapi.TYPE_STRING, description='Note de l\'avis'),
                'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Commentaire de l\'avis'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='ID de l\'utilisateur')
            }
        ),
        responses={
            200: RatingSerializer,
            404: openapi.Response('Avis non trouvé'),
            500: 'Internal Server Error'
        }
    )
    def put(self, request, rating_id):
        rating = self.get_object(rating_id=rating_id)
        # variables
        score = request.data.get("score")
        comment = request.data.get("comment")
        user = request.data.get("user")

        #  score
        if score:
            rating.score = score
            rating.save()

        #  comment
        if comment:
            rating.comment = comment
            rating.save()

        #  user
        if user:
            user_value = get_object_or_404(ProfilUser, id=user)
            rating.user = user_value
            rating.save()

        serializer = RatingSerializer(rating, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Supprime un avis par son ID",
        manual_parameters=[
            openapi.Parameter(
                'rating_id',
                openapi.IN_PATH,
                description="Identifiant unique de l'avis",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: 'Avis supprimé avec succès',
            404: openapi.Response('Avis non trouvé'),
            500: 'Internal Server Error'
        }
    )
    def delete(self, request, rating_id):
        rating = self.get_object(rating_id=rating_id)
        rating.delete()
        return Response(
            {"message": "rating is deleted"}, status=status.HTTP_204_NO_CONTENT
        )
