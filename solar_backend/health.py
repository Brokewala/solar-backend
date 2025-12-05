from django.http import HttpResponse
from django.db import connections, OperationalError


def health_view(request):
    return HttpResponse("ok")


def readiness(request):
    try:
        connections["default"].cursor()
    except OperationalError:
        return HttpResponse("unavailable", status=503)
    return HttpResponse("ok")
