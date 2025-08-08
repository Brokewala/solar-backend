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
from .models import Report
from .models import ReportComment
from .models import ReportState

# serializer
from .serializers import ReportSerializer
from .serializers import ReportCommentSerializer
from .serializers import ReportStateSerializer

# view
@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les rapports",
    responses={
        200: ReportSerializer(many=True),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_Report(request):
    report_data = Report.objects.all().order_by("-createdAt")
    serializer = ReportSerializer(report_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_description="Récupère tous les rapports d'un utilisateur",
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
        200: ReportSerializer(many=True),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_report_by_user(request, user_id):
    report_data = Report.objects.filter(user__id=user_id)
    serializer = ReportSerializer(report_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Report APIView
class ReportAPIView(APIView):

    def get_object(self, report_id):
        try:
            return Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        description = request.data.get("description")
        priority = request.data.get("priority")
        user = request.data.get("user")
        closed = request.data.get("closed")
        closed_str = str(closed).strip().lower() == "true"
        
        if user is None or closed is None or description is None or priority is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get user
        user_data = get_object_or_404(ProfilUser, id=user)

        # create user
        report_data = Report.objects.create(
            description=description,
            priority=priority,
            closed=closed_str,
            user=user_data,
        )
        # save into database
        report_data.save()

        serializer = ReportSerializer(report_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, report_id):
        report_data = self.get_object(report_id=report_id)
        serializer = ReportSerializer(report_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, report_id):
        report_data = self.get_object(report_id=report_id)
        # variables
        description = request.data.get("description")
        priority = request.data.get("priority")
        closed = request.data.get("closed")

        #  description
        if description:
            report_data.description = description
            report_data.save()

        #  priority
        if priority:
            report_data.priority = priority
            report_data.save()

        #  closed
        if closed:
            report_data.closed = closed
            report_data.save()

        serializer = ReportSerializer(report_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, report_id):
        report_data = self.get_object(report_id=report_id)
        report_data.delete()
        return Response(
            {"message": "report is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# ReportComment
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_reportComment_by_report(request, report_id):
    report_data = ReportComment.objects.filter(report__id=report_id)
    serializer = ReportCommentSerializer(report_data, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ReportComment
class ReportCommentAPIView(APIView):

    def get_object(self, comment_id):
        try:
            return ReportComment.objects.get(id=comment_id)
        except ReportComment.DoesNotExist:
            return Response(
                {"error": "Report Comment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        sender_id = request.data.get("sender_id")
        report_id = request.data.get("report_id")
        description = request.data.get("description")

        if description is None or sender_id is None or description is None or report_id is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get 
        sender = get_object_or_404(ProfilUser, id=sender_id)
        report = get_object_or_404(Report, id=report_id)

        # create comment
        comment_data = ReportComment.objects.create(
            description=description,
            report=report,
            sender=sender,
        )
        # save into database
        comment_data.save()

        serializer = ReportCommentSerializer(comment_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, comment_id):
        comment_data = self.get_object(comment_id=comment_id)
        serializer = ReportCommentSerializer(comment_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, comment_id):
        comment_data = self.get_object(comment_id=comment_id)
        # variables
        description = request.data.get("description")

        #  description
        if description:
            comment_data.description = description
            comment_data.save()

        serializer = ReportCommentSerializer(comment_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):
        comment_data = self.get_object(comment_id=comment_id)
        comment_data.delete()
        return Response(
            {"message": "report comment is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# ReportState
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_ReportState_by_report(request, report_id):
    report_data = ReportState.objects.get(report__id=report_id)
    serializer = ReportStateSerializer(report_data, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ReportState
class ReportStateAPIView(APIView):

    def get_object(self, state_id):
        try:
            return ReportState.objects.get(id=state_id)
        except ReportState.DoesNotExist:
            return Response(
                {"error": "Report State not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        report_id = request.data.get("report_id")
        state = request.data.get("state")
        value = request.data.get("value")

        if value is None or state is None or report_id is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )

        # get 
        report = get_object_or_404(Report, id=report_id)

        # create report state
        state_data = ReportState.objects.create(
            value=value,
            report=report,
            state=state,
        )
        # save into database
        state_data.save()

        serializer = ReportStateSerializer(state_data, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, state_id):
        report_data = self.get_object(state_id=state_id)
        serializer = ReportStateSerializer(report_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, state_id):
        report_data = self.get_object(state_id=state_id)
        # variables
        state = request.data.get("state")
        value = request.data.get("value")

        #  state
        if state:
            report_data.state = state
            report_data.save()
        
        #  value
        if value:
            report_data.value = value
            report_data.save()

        serializer = ReportStateSerializer(report_data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, state_id):
        report_data = self.get_object(state_id=state_id)
        report_data.delete()
        return Response(
            {"message": "report comment is deleted"}, status=status.HTTP_204_NO_CONTENT
        )

