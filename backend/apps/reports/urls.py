from django.urls import path
from .views import (
    MonthlyAttendanceReportPDFView, MonthlyAttendanceReportDOCXView,
    DeficiencyReportCSVView
)

urlpatterns = [
    path('monthly/pdf/', MonthlyAttendanceReportPDFView.as_view(), name='report-monthly-pdf'),
    path('monthly/docx/', MonthlyAttendanceReportDOCXView.as_view(), name='report-monthly-docx'),
    path('deficiency/csv/', DeficiencyReportCSVView.as_view(), name='report-deficiency-csv'),
]
