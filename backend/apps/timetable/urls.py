from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimetableSlotViewSet, LectureSessionViewSet

router = DefaultRouter()
router.register(r'slots', TimetableSlotViewSet, basename='timetable-slot')
router.register(r'sessions', LectureSessionViewSet, basename='lecture-session')

urlpatterns = [
    path('', include(router.urls)),
]
