from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacultyAssignmentViewSet

router = DefaultRouter()
router.register(r'assignments', FacultyAssignmentViewSet, basename='faculty-assignment')

urlpatterns = [
    path('', include(router.urls)),
]
