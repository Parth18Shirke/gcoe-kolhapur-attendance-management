import io
import csv
from typing import Dict, Any, List
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from apps.academics.models import Division
from .models import Student, StudentImportLog

def parse_student_file(file_obj, default_division_id=None, uploaded_by=None) -> Dict[str, Any]:
    """
    Parses a CSV or Excel (.xlsx) file and non-destructively upserts students into the database.
    """
    filename = getattr(file_obj, 'name', 'uploaded_roster.csv')
    content = file_obj.read()
    
    rows: List[Dict[str, str]] = []

    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        sheet = wb.active
        header = None
        for row in sheet.iter_rows(values_only=True):
            if not row or all(cell is None for cell in row):
                continue
            if header is None:
                header = [str(c).strip().lower().replace(" ", "_") if c is not None else "" for c in row]
                continue
            row_dict = {header[i]: str(row[i]).strip() if i < len(row) and row[i] is not None else "" for i in range(len(header))}
            rows.append(row_dict)
    else:
        # Assume CSV / Text
        try:
            text_stream = io.StringIO(content.decode('utf-8-sig'))
        except UnicodeDecodeError:
            text_stream = io.StringIO(content.decode('latin-1'))
        reader = csv.DictReader(text_stream)
        for r in reader:
            normalized = {k.strip().lower().replace(" ", "_"): v.strip() for k, v in r.items() if k}
            rows.append(normalized)

    total_rows = len(rows)
    imported_count = 0
    updated_count = 0
    error_count = 0
    error_details = []

    # Column aliases
    def extract_val(d, keys, default=""):
        for k in keys:
            if k in d and d[k]:
                return d[k]
        return default

    with transaction.atomic():
        import_log = StudentImportLog.objects.create(
            uploaded_by=uploaded_by,
            file_name=filename,
            total_rows=total_rows
        )

        for idx, row in enumerate(rows, start=2): # 1-indexed row number in spreadsheet
            prn = extract_val(row, ['prn', 'university_prn', 'registration_number', 'student_id'])
            roll_no = extract_val(row, ['roll_number', 'roll_no', 'roll'])
            name = extract_val(row, ['full_name', 'student_name', 'name'])
            email = extract_val(row, ['official_email', 'email', 'college_email']).lower()
            division_name = extract_val(row, ['division', 'division_name', 'class'])

            if not prn or not roll_no or not name or not email:
                error_count += 1
                error_details.append({
                    'row': idx,
                    'error': f"Missing required fields. Required: PRN, Roll No, Full Name, Email. Got: PRN='{prn}', Roll='{roll_no}', Name='{name}', Email='{email}'"
                })
                continue

            try:
                validate_email(email)
            except ValidationError:
                error_count += 1
                error_details.append({'row': idx, 'error': f"Invalid email format: '{email}'"})
                continue

            target_division = None
            if default_division_id:
                try:
                    target_division = Division.objects.get(id=default_division_id)
                except Division.DoesNotExist:
                    pass

            if not target_division and division_name:
                target_division = Division.objects.filter(name__iexact=division_name).first()

            if not target_division:
                # Fallback: grab any existing division or report error
                target_division = Division.objects.first()
                if not target_division:
                    error_count += 1
                    error_details.append({'row': idx, 'error': "No academic division available in system to assign student."})
                    continue

            # Upsert student based on immutable PRN
            student, created = Student.objects.update_or_create(
                prn=prn,
                defaults={
                    'roll_number': roll_no,
                    'full_name': name,
                    'official_email': email,
                    'division': target_division,
                    'status': 'ACTIVE',
                }
            )

            if created:
                imported_count += 1
            else:
                updated_count += 1

        import_log.imported_count = imported_count
        import_log.updated_count = updated_count
        import_log.error_count = error_count
        import_log.error_details = error_details
        import_log.save()

    return {
        'import_log_id': import_log.id,
        'total_rows': total_rows,
        'imported': imported_count,
        'updated': updated_count,
        'errors': error_count,
        'error_details': error_details[:50] # truncated for summary response
    }
