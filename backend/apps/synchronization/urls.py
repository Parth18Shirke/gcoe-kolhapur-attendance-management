from django.urls import path
from .views import OfflineSyncAttendanceView

urlpatterns = [
    path('attendance/', OfflineSyncAttendanceView.as_view(), name='sync-attendance'),
]
