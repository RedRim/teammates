from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from decouple import config

urlpatterns = [
    path(str(config('ADMIN_URL')), admin.site.urls),
    path('', include('chat.urls')),
    path('', include('account.urls')),
    path('', include('people.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
