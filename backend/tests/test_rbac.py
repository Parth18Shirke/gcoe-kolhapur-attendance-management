import pytest

@pytest.mark.django_db
def test_unauthenticated_access_denied(api_client):
    resp = api_client.get('/api/v1/academics/departments/')
    assert resp.status_code == 401

@pytest.mark.django_db
def test_user_management_rbac(auth_client_admin, auth_client_hod, auth_client_faculty):
    # Admin can list users
    resp_admin = auth_client_admin.get('/api/v1/auth/users/')
    assert resp_admin.status_code == 200

    # HOD cannot manage users
    resp_hod = auth_client_hod.get('/api/v1/auth/users/')
    assert resp_hod.status_code == 403

    # Faculty cannot manage users
    resp_faculty = auth_client_faculty.get('/api/v1/auth/users/')
    assert resp_faculty.status_code == 403

@pytest.mark.django_db
def test_department_creation_restricted_to_admin(auth_client_admin, auth_client_hod, auth_client_faculty):
    payload = {'name': 'Mechanical Engineering', 'code': 'ME'}

    # Faculty cannot create department
    resp_faculty = auth_client_faculty.post('/api/v1/academics/departments/', payload)
    assert resp_faculty.status_code == 403

    # HOD cannot create department
    resp_hod = auth_client_hod.post('/api/v1/academics/departments/', payload)
    assert resp_hod.status_code == 403

    # Admin can create department
    resp_admin = auth_client_admin.post('/api/v1/academics/departments/', payload)
    assert resp_admin.status_code == 201
    assert resp_admin.data['code'] == 'ME'
