from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.conf import settings
from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="SolarNative API",
      default_version='v1',
      description="Documentation de l'API de SolarNative (battery, prise, panneau)",
      contact=openapi.Contact(email="support@tonsite.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/solar/users/', include("users.urls")),
    path('api/solar/modules/', include("module.urls")),
    path('api/solar/rating/', include("rating.urls")),
    path('api/solar/battery/', include("battery.urls")),
    path('api/solar/panneau/', include("panneau.urls")),
    path('api/solar/prise/', include("prise.urls")),
    path('api/solar/report/', include("report.urls")),
    path('api/solar/subscription/', include("subscription.urls")),
    path('api/solar/notification/', include("notification.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]