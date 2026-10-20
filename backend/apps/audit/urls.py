from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditEntryViewSet

router = DefaultRouter()
router.register(r'logs', AuditEntryViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
]
