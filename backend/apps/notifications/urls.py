from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationOutboxViewSet, ProcessOutboxView, NotificationStateViewSet

router = DefaultRouter()
router.register(r'outbox', NotificationOutboxViewSet, basename='notification-outbox')
router.register(r'states', NotificationStateViewSet, basename='notification-state')

urlpatterns = [
    path('outbox/process/', ProcessOutboxView.as_view(), name='notification-process'),
    path('', include(router.urls)),
]
