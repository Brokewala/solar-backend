from rest_framework import status

# from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404

# models
from .models import Modules
from .models import ModulesInfo
from .models import ModulesDetail
from users.models import ProfilUser

# serializer
from .serializers import ModulesSerializer
from .serializers import ModulesInfoSerializer
from .serializers import ModulesDetailSerializer


# get all module
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_all_module(request):
    modules = Modules.objects.all().order_by("-createdAt")
    serializer = ModulesSerializer(modules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# get all module
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_module_by_user(request, user_id):
    modules = Modules.objects.get(user__id=user_id)
    serializer = ModulesSerializer(modules, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Modules APIView
class ModulesAPIView(APIView):

    def get_object(self, module_id):
        try:
            return Modules.objects.get(id=module_id)
        except Modules.DoesNotExist:
            return Response(
                {"error": "module not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        gr_code = request.FILES.get("gr_code")
        name = request.data.get("name")
        identifiant = request.data.get("identifiant")
        password = request.data.get("password")
        user = request.data.get("user")
        if name is None or identifiant is None or password is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # create user
        module = Modules.objects.create(
            name=request.data["name"],
            identifiant=request.data["identifiant"],
            password=request.data["password"],
        )
        # save into database
        module.save()

        #  gr_code
        if gr_code:
            module.gr_code = gr_code
            module.save()

        #  user
        if user:
            user_value = get_object_or_404(ProfilUser, id=user)
            module.user = user_value
            module.save()

        serializer = ModulesSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, module_id):
        module = self.get_object(module_id=module_id)
        serializer = ModulesSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, module_id):
        module = self.get_object(module_id=module_id)
        # variables
        gr_code = request.FILES.get("gr_code")
        name = request.data.get("name")
        identifiant = request.data.get("identifiant")
        password = request.data.get("password")
        user = request.data.get("user")

        #  gr_code
        if gr_code:
            module.gr_code = gr_code
            module.save()

        #  gr_code
        if name:
            module.name = name
            module.save()

        #  gr_code
        if identifiant:
            module.identifiant = identifiant
            module.save()

        #  gr_code
        if password:
            module.password = password
            module.save()

        #  user
        if user:
            user_value = get_object_or_404(ProfilUser, id=user)
            module.user = user_value
            module.save()

        serializer = ModulesSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, module_id):
        module = self.get_object(module_id=module_id)
        module.delete()
        return Response(
            {"message": "module is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all ModulesInfo
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_moduleinfo_by_module(request, module_id):
    modules_info = ModulesInfo.objects.get(module__id=module_id)
    serializer = ModulesInfoSerializer(modules_info, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ModulesInfo APIView
class ModulesInfoAPIView(APIView):

    def get_object(self, module_id):
        try:
            return ModulesInfo.objects.get(id=module_id)
        except ModulesInfo.DoesNotExist:
            return Response(
                {"error": "modules Info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        module = request.data.get("module")
        name = request.data.get("name")
        description = request.data.get("description")
        if name is None or module is None or description is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get module
        module_data =get_object_or_404(Modules, id=module)
        
        module_info = ModulesInfo.objects.create(
            name=name,
            module=module_data,
            description=description,
        )
        # save into database
        module_info.save()
        serializer = ModulesInfoSerializer(module_info, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, module_id):
        module = self.get_object(module_id=module_id)
        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, module_id):
        module = self.get_object(module_id=module_id)
        # variables
        name = request.data.get("name")
        description = request.data.get("description")

        #  gr_code
        if name:
            module.name = name
            module.save()

        #  description
        if description:
            module.description = description
            module.save()

        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, module_id):
        module = self.get_object(module_id=module_id)
        module.delete()
        return Response(
            {"message": "module is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


# get all ModulesDetail
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def get_one_moduledetail_by_module(request, module_id):
    modules_detail = ModulesDetail.objects.get(module_info__id=module_id)
    serializer = ModulesDetailSerializer(modules_detail, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

# ModulesDetail APIView
class ModulesDetailAPIView(APIView):

    def get_object(self, module_id):
        try:
            return ModulesDetail.objects.get(id=module_id)
        except ModulesDetail.DoesNotExist:
            return Response(
                {"error": "modules detail not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        module_info = request.data.get("module_info")
        value = request.data.get("value")
        description = request.data.get("description")
        if value is None or module_info is None or description is None:
            return Response(
                {"error": "All input is request"}, status=status.HTTP_400_BAD_REQUEST
            )
        # get module
        module_data =get_object_or_404(ModulesInfo, id=module_info)
        
        module_detail = ModulesInfo.objects.create(
            value=value,
            module_info=module_data,
            description=description,
        )
        # save into database
        module_detail.save()
        serializer = ModulesInfoSerializer(module_detail, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, module_id):
        module = self.get_object(module_id=module_id)
        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, module_id):
        module = self.get_object(module_id=module_id)
        # variables
        name = request.data.get("name")
        description = request.data.get("description")

        #  gr_code
        if name:
            module.name = name
            module.save()

        #  description
        if description:
            module.description = description
            module.save()

        serializer = ModulesInfoSerializer(module, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, module_id):
        module = self.get_object(module_id=module_id)
        module.delete()
        return Response(
            {"message": "module is deleted"}, status=status.HTTP_204_NO_CONTENT
        )

