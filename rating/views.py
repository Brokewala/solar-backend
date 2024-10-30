from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404

# models
from users.models import ProfilUser
from .models import Rating

# serializer
from .serializers import RatingSerializer


# get all Rating
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_rating(request):
    ratings = Rating.objects.all().order_by("-createdAt")
    serializer = RatingSerializer(ratings, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# get all module
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_rating_by_user(request, user_id):
    ratings = Rating.objects.get(user=user_id)
    serializer = RatingSerializer(ratings, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


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

        # create user
        module = Rating.objects.create(
            score=score,
            comment=comment,
            user=user_value,
        )
        # save into database
        module.save()

        serializer = RatingSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, rating_id):
        module = self.get_object(rating_id=rating_id)
        serializer = RatingSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    def delete(self, request, rating_id):
        rating = self.get_object(rating_id=rating_id)
        rating.delete()
        return Response(
            {"message": "rating is deleted"}, status=status.HTTP_204_NO_CONTENT
        )
