from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('superuser/', admin.site.urls),
    path('', include("dashboard.urls")),
    path('accounts/', include("accounts.urls")),
    path('staff/', include("staff.urls")),
    path('student/', include("student.urls")),
    path('results/', include("pdfgenerator.urls")),
    path('sms/', include("sms.urls")),
    path('api/', include("api.urls")),
    path('school/', include("school.urls")),
]

admin.site.site_header = "KETASCO - DATABASE ADMINISTRATOR" # default: "Django Administration"
admin.site.index_title = "Administrator"                    # default: "Site administration"
admin.site.site_title =  'Super User'                # default: "Django site admin"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)