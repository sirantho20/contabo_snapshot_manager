from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Serve static files in development/production
if settings.DEBUG or True:  # Always serve static files for admin
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 