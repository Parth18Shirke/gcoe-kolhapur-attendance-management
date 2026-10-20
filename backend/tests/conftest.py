import pytest
from datetime import date, time
from rest_framework.test import APIClient
from apps.accounts.models import User, UserToken
from apps.academics.models import Department, Program, AcademicYear, Semester, Division, Subject
from apps.rooms.models import Room
from apps.students.models import Student

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def department(db):
    return Department.objects.create(name="Information Technology", code="IT")

@pytest.fixture
def admin_user(db, department):
    return User.objects.create_user(
        email="admin.test@college.edu",
        full_name="Admin User",
        role="ADMIN",
        department=department,
        is_staff=True,
        is_superuser=True
    )

@pytest.fixture
def hod_user(db, department):
    return User.objects.create_user(
        email="hod.test@college.edu",
        full_name="HOD User",
        role="HOD",
        department=department
    )

@pytest.fixture
def faculty_user(db, department):
    return User.objects.create_user(
        email="faculty.test@college.edu",
        full_name="Faculty User",
        role="FACULTY",
        department=department
    )

@pytest.fixture
def other_faculty_user(db, department):
    return User.objects.create_user(
        email="faculty2.test@college.edu",
        full_name="Other Faculty",
        role="FACULTY",
        department=department
    )

@pytest.fixture
def faculty_token(faculty_user):
    return UserToken.generate(faculty_user)

@pytest.fixture
def hod_token(hod_user):
    return UserToken.generate(hod_user)

@pytest.fixture
def admin_token(admin_user):
    return UserToken.generate(admin_user)

@pytest.fixture
def auth_client_faculty(faculty_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {faculty_token.key}")
    return client

@pytest.fixture
def auth_client_hod(hod_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {hod_token.key}")
    return client

@pytest.fixture
def auth_client_admin(admin_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token.key}")
    return client

@pytest.fixture
def academic_setup(db, department):
    prog = Program.objects.create(department=department, name="B.Tech IT", code="BTECH-IT")
    ay = AcademicYear.objects.create(name="2026-2027", start_date=date(2026, 7, 1), end_date=date(2027, 5, 31), is_current=True)
    sem = Semester.objects.create(program=prog, academic_year=ay, semester_number=5, term_type='ODD', is_current=True)
    div = Division.objects.create(semester=sem, name="Division A")
    sub_theory = Subject.objects.create(department=department, semester=sem, name="Database Systems", code="CS301", subject_type='THEORY')
    sub_lab = Subject.objects.create(department=department, semester=sem, name="DBMS Lab", code="CS302", subject_type='LAB')
    room_class = Room.objects.create(name="Room 204", room_type='CLASSROOM', capacity=70)
    room_lab = Room.objects.create(name="Lab 3", room_type='LAB', capacity=40)

    students = []
    for i in range(1, 5):
        s = Student.objects.create(
            prn=f"2306036124100{i}",
            roll_number=f"IT-0{i}",
            full_name=f"Student {i}",
            official_email=f"student{i}@college.edu",
            division=div,
            status='ACTIVE'
        )
        students.append(s)

    return {
        'program': prog,
        'academic_year': ay,
        'semester': sem,
        'division': div,
        'subject_theory': sub_theory,
        'subject_lab': sub_lab,
        'room_class': room_class,
        'room_lab': room_lab,
        'students': students
    }
