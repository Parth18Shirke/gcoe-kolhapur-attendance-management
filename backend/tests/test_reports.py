import pytest

@pytest.mark.django_db
def test_pdf_report_generation(auth_client_faculty, academic_setup):
    div = academic_setup['division']
    resp = auth_client_faculty.get(f'/api/v1/reports/monthly/pdf/?division_id={div.id}')
    assert resp.status_code == 200
    assert resp['Content-Type'] == 'application/pdf'
    assert resp.content.startswith(b'%PDF') # PDF magic bytes

@pytest.mark.django_db
def test_docx_report_generation(auth_client_faculty, academic_setup):
    div = academic_setup['division']
    resp = auth_client_faculty.get(f'/api/v1/reports/monthly/docx/?division_id={div.id}')
    assert resp.status_code == 200
    assert 'wordprocessingml.document' in resp['Content-Type']
    assert resp.content.startswith(b'PK') # DOCX zip container magic bytes

@pytest.mark.django_db
def test_deficiency_csv_export(auth_client_faculty, academic_setup):
    div = academic_setup['division']
    resp = auth_client_faculty.get(f'/api/v1/reports/deficiency/csv/?division_id={div.id}')
    assert resp.status_code == 200
    assert 'text/csv' in resp['Content-Type']
    assert "Roll No,PRN (Last 4),Student Name" in resp.content.decode('utf-8')
