"""Project-level utility views."""

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def debug_time_view(request):
    """Return the current local and UTC timestamps for debugging."""

    now = timezone.now()
    return Response(
        {
            "now_local": timezone.localtime(now).isoformat(),
            "now_utc": now.astimezone(timezone.utc).isoformat(),
        }
    )
