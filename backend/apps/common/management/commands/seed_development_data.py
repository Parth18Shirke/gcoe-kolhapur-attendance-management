from datetime import date, time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from apps.accounts.models import User
from apps.academics.models import Department, Program, AcademicYear, Semester, Division, Subject
from apps.rooms.models import Room
from apps.students.models import Student
from apps.faculty.models import FacultyAssignment
from apps.timetable.models import TimetableSlot

class Command(BaseCommand):
    help = "Seeds clean mock academic fixtures for DEVELOPMENT AND TESTING ONLY. Do NOT run in production."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("================================================================="))
        self.stdout.write(self.style.WARNING("SEEDING DEVELOPMENT & TEST FIXTURES ONLY (NOT FOR PRODUCTION)"))
        self.stdout.write(self.style.WARNING("================================================================="))

        with transaction.atomic():
            # 1. Department
            dept, _ = Department.objects.get_or_create(
                code='IT',
                defaults={'name': 'Department of Information Technology', 'description': 'Academic IT Dept'}
            )

            # 2. Roles & Users
            admin_user, _ = User.objects.get_or_create(
                email='admin@college.edu',
                defaults={'full_name': 'System Administrator', 'role': 'ADMIN', 'is_staff': True, 'is_superuser': True}
            )
            admin_user.set_password('Admin@AMS2026!')
            admin_user.save()

            hod_user, _ = User.objects.get_or_create(
                email='hod.it@college.edu',
                defaults={'full_name': 'Dr. V. M. Deshmukh', 'role': 'HOD', 'department': dept, 'is_staff': False}
            )

            faculty_user, _ = User.objects.get_or_create(
                email='faculty.kulkarni@college.edu',
                defaults={'full_name': 'Prof. S. R. Kulkarni', 'role': 'FACULTY', 'department': dept, 'is_staff': False}
            )

            # 3. Academic Structure
            program, _ = Program.objects.get_or_create(
                code='BTECH-IT',
                defaults={'department': dept, 'name': 'Bachelor of Technology (IT)', 'duration_years': 4}
            )

            ay, _ = AcademicYear.objects.get_or_create(
                name='2026-2027',
                defaults={'start_date': date(2026, 7, 1), 'end_date': date(2027, 5, 31), 'is_current': True}
            )

            sem, _ = Semester.objects.get_or_create(
                program=program,
                academic_year=ay,
                semester_number=5,
                defaults={'term_type': 'ODD', 'is_current': True}
            )

            div, _ = Division.objects.get_or_create(
                semester=sem,
                name='Division A',
                defaults={'code': 'DIV-A'}
            )

            # 4. Subjects & Rooms
            sub_dbms, _ = Subject.objects.get_or_create(
                semester=sem,
                code='CS301',
                defaults={'department': dept, 'name': 'Database Management Systems', 'subject_type': 'THEORY', 'weekly_theory_hours': 3}
            )

            sub_lab, _ = Subject.objects.get_or_create(
                semester=sem,
                code='CS302',
                defaults={'department': dept, 'name': 'DBMS Laboratory', 'subject_type': 'LAB', 'weekly_lab_hours': 2}
            )

            room_204, _ = Room.objects.get_or_create(
                name='Room 204',
                defaults={'room_type': 'CLASSROOM', 'capacity': 70, 'building': 'Academic Block A', 'floor': '2nd Floor'}
            )

            lab_3, _ = Room.objects.get_or_create(
                name='Lab 3',
                defaults={'room_type': 'LAB', 'capacity': 40, 'building': 'IT Complex', 'floor': 'Ground Floor'}
            )

            # 5. Workload Allocation
            FacultyAssignment.objects.get_or_create(
                faculty=faculty_user,
                subject=sub_dbms,
                division=div,
                academic_year=ay,
                defaults={'is_primary': True}
            )

            # 6. Sample Dev Students
            for i in range(1, 11):
                roll = f"IT-{i:02d}"
                prn = f"2306036124{1000 + i}"
                Student.objects.get_or_create(
                    prn=prn,
                    defaults={
                        'roll_number': roll,
                        'full_name': f"Dev Test Student {i}",
                        'official_email': f"student{i}@college.edu",
                        'division': div,
                        'status': 'ACTIVE'
                    }
                )

            # 7. Timetable Slots
            TimetableSlot.objects.get_or_create(
                academic_year=ay,
                division=div,
                subject=sub_dbms,
                faculty=faculty_user,
                room=room_204,
                day_of_week=0, # Monday
                start_time=time(10, 0),
                end_time=time(11, 0),
                defaults={'session_type': 'THEORY', 'is_active': True}
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded development and test academic fixtures!"))
        self.stdout.write(self.style.SUCCESS("Users created:"))
        self.stdout.write("  - Admin:   admin@college.edu (Password: Admin@AMS2026!)")
        self.stdout.write("  - HOD:     hod.it@college.edu (Uses Email OTP)")
        self.stdout.write("  - Faculty: faculty.kulkarni@college.edu (Uses Email OTP)")
