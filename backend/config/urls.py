from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI Schema & Interactive Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Modular Domain APIs (v1)
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/academics/', include('apps.academics.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/faculty/', include('apps.faculty.urls')),
    path('api/v1/rooms/', include('apps.rooms.urls')),
    path('api/v1/timetable/', include('apps.timetable.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    path('api/v1/corrections/', include('apps.corrections.urls')),
    path('api/v1/sync/', include('apps.synchronization.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
]
