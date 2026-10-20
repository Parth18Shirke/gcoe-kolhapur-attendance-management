from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentImportView, StudentImportLogViewSet

router = DefaultRouter()
router.register(r'records', StudentViewSet, basename='student')
router.register(r'import-logs', StudentImportLogViewSet, basename='student-import-log')

urlpatterns = [
    path('import/', StudentImportView.as_view(), name='student-import'),
    path('', include(router.urls)),
]
