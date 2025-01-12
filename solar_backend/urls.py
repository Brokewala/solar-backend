from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings
from django.contrib import admin

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
