import io
import pytest
from apps.students.models import Student
from apps.students.services import parse_student_file

@pytest.mark.django_db
def test_student_prn_privacy_in_classroom_view(auth_client_faculty, auth_client_admin, academic_setup):
    div = academic_setup['division']

    # Faculty list: should only expose last_4_prn and classroom_display
    resp_faculty = auth_client_faculty.get(f'/api/v1/students/records/?division={div.id}')
    assert resp_faculty.status_code == 200
    first_student = resp_faculty.data['results'][0]
    assert 'prn' not in first_student # Full PRN hidden from classroom view
    assert 'last_4_prn' in first_student
    assert 'classroom_display' in first_student
    assert first_student['last_4_prn'] == '1001'
    assert first_student['classroom_display'] == '1001 — Student 1'

    # Admin list: exposes full PRN
    resp_admin = auth_client_admin.get(f'/api/v1/students/records/?division={div.id}')
    assert resp_admin.status_code == 200
    admin_student = resp_admin.data['results'][0]
    assert 'prn' in admin_student
    assert admin_student['prn'] == '23060361241001'

@pytest.mark.django_db
def test_student_csv_import_service(academic_setup, admin_user):
    div = academic_setup['division']
    csv_content = (
        "prn,roll_number,full_name,official_email,division\n"
        "23060361242001,IT-21,Rohan Kulkarni,rohan.k@college.edu,Division A\n"
        "23060361242002,IT-22,Pooja Patil,pooja.p@college.edu,Division A\n"
    )
    file_obj = io.BytesIO(csv_content.encode('utf-8'))
    file_obj.name = "roster.csv"

    res = parse_student_file(file_obj, default_division_id=div.id, uploaded_by=admin_user)
    assert res['total_rows'] == 2
    assert res['imported'] == 2
    assert res['errors'] == 0

    student1 = Student.objects.get(prn="23060361242001")
    assert student1.full_name == "Rohan Kulkarni"
    assert student1.last_4_prn == "2001"
    assert student1.classroom_display == "2001 — Rohan Kulkarni"
