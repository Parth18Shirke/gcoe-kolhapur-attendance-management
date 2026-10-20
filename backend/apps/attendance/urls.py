from django.urls import path
from .views import (
    SessionRosterView, SubmitSessionAttendanceView,
    StudentAttendanceMetricView, DivisionAttendanceSummaryView
)

urlpatterns = [
    path('sessions/<int:session_id>/roster/', SessionRosterView.as_view(), name='session-roster'),
    path('sessions/<int:session_id>/submit/', SubmitSessionAttendanceView.as_view(), name='session-submit'),
    path('students/<int:student_id>/metrics/', StudentAttendanceMetricView.as_view(), name='student-metrics'),
    path('divisions/<int:division_id>/summary/', DivisionAttendanceSummaryView.as_view(), name='division-summary'),
]
