from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema
from apps.academics.models import Division, Subject
from apps.students.models import Student
from apps.attendance.services import calculate_student_attendance
from .builders.pdf_builder import generate_attendance_pdf
from .builders.docx_builder import generate_attendance_docx
from .builders.csv_builder import generate_attendance_csv

def build_report_data(division_id, subject_id=None):
    division = Division.objects.select_related('semester').get(id=division_id)
    subject = Subject.objects.get(id=subject_id) if subject_id else None

    sub_title = f"{division.name} ({division.semester})"
    if subject:
        sub_title += f" | {subject.code} - {subject.name}"

    students = Student.objects.filter(division=division, status='ACTIVE').order_by('roll_number')
    headers = ["Roll No", "PRN (Last 4)", "Student Name", "Conducted", "Attended", "Absent", "Theory %", "Lab %", "Overall %", "Status"]

    rows = []
    for s in students:
        m = calculate_student_attendance(s, subject_id=subject.id if subject else None)
        stat = "DEFICIENT" if m['is_deficient'] else "NORMAL"
        rows.append([
            s.roll_number,
            s.last_4_prn,
            s.full_name,
            m['total_conducted'],
            m['total_attended'],
            m['total_absent'],
            f"{m['theory_percentage']}%",
            f"{m['lab_percentage']}%",
            f"{m['overall_percentage']}%",
            stat
        ])

    return division, subject, sub_title, headers, rows

class MonthlyAttendanceReportPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={(200, 'application/pdf'): bytes})
    def get(self, request):
        div_id = request.query_params.get('division_id')
        sub_id = request.query_params.get('subject_id')
        if not div_id:
            return Response({'success': False, 'error': {'code': 'MISSING_PARAM', 'message': 'division_id query parameter is required.'}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            division, subject, sub_title, headers, rows = build_report_data(div_id, sub_id)
            pdf_buf = generate_attendance_pdf(
                report_title="MONTHLY ATTENDANCE STATEMENT",
                subtitle=sub_title,
                headers=headers,
                rows=rows,
                is_landscape=True
            )
            response = HttpResponse(pdf_buf.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Monthly_Attendance_{division.name.replace(" ", "_")}.pdf"'
            return response
        except Division.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Division not found.'}}, status=status.HTTP_404_NOT_FOUND)

class MonthlyAttendanceReportDOCXView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={(200, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'): bytes})
    def get(self, request):
        div_id = request.query_params.get('division_id')
        sub_id = request.query_params.get('subject_id')
        if not div_id:
            return Response({'success': False, 'error': {'code': 'MISSING_PARAM', 'message': 'division_id query parameter is required.'}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            division, subject, sub_title, headers, rows = build_report_data(div_id, sub_id)
            docx_buf = generate_attendance_docx(
                report_title="OFFICIAL ATTENDANCE REPORT",
                subtitle=sub_title,
                headers=headers,
                rows=rows
            )
            response = HttpResponse(docx_buf.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="Attendance_Report_{division.name.replace(" ", "_")}.docx"'
            return response
        except Division.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Division not found.'}}, status=status.HTTP_404_NOT_FOUND)

class DeficiencyReportCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={(200, 'text/csv'): str})
    def get(self, request):
        div_id = request.query_params.get('division_id')
        sub_id = request.query_params.get('subject_id')
        if not div_id:
            return Response({'success': False, 'error': {'code': 'MISSING_PARAM', 'message': 'division_id query parameter is required.'}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            division, subject, sub_title, headers, rows = build_report_data(div_id, sub_id)
            # Filter strictly for deficient rows (< 75%)
            deficient_rows = [r for r in rows if r[-1] == 'DEFICIENT']
            csv_stream = generate_attendance_csv(headers, deficient_rows)

            response = HttpResponse(csv_stream.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="Deficiency_Warning_Report_{division.name.replace(" ", "_")}.csv"'
            return response
        except Division.DoesNotExist:
            return Response({'success': False, 'error': {'code': 'NOT_FOUND', 'message': 'Division not found.'}}, status=status.HTTP_404_NOT_FOUND)
