from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .health import health, readiness

schema_view = get_schema_view(
   openapi.Info(
      title="Solar API",
      default_version='v1',
      description="API complète pour la gestion de plateforme solaire. Cette API permet de gérer les batteries, panneaux solaires, prises électriques, planifications et notifications pour un système de production d'énergie solaire.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@solar-platform.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    #
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
    path('readiness/', readiness, name='readiness'),
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

