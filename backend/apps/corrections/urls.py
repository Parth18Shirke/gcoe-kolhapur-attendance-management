from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubmitCorrectionView, CorrectionRequestViewSet, ReviewCorrectionView

router = DefaultRouter()
router.register(r'requests', CorrectionRequestViewSet, basename='correction-request')

urlpatterns = [
    path('request/', SubmitCorrectionView.as_view(), name='correction-request-submit'),
    path('requests/<int:pk>/review/', ReviewCorrectionView.as_view(), name='correction-review'),
    path('', include(router.urls)),
]
