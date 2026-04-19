from fastapi.testclient import TestClient


def login(client: TestClient, username: str, password: str):
    return client.post(
        '/api/v1/auth/login',
        json={'username': username, 'password': password},
    )


def test_login_success_and_me_endpoint(anonymous_client: TestClient):
    response = login(anonymous_client, 'admin', 'labosadmin')
    assert response.status_code == 200
    payload = response.json()
    assert payload['user']['username'] == 'admin'
    assert payload['user']['role'] == 'admin'
    assert payload['access_token']

    me_response = anonymous_client.get('/api/v1/auth/me')
    assert me_response.status_code == 200
    assert me_response.json()['username'] == 'admin'


def test_logout_clears_session_cookie(anonymous_client: TestClient):
    response = login(anonymous_client, 'admin', 'labosadmin')
    assert response.status_code == 200

    logout_response = anonymous_client.post('/api/v1/auth/logout')
    assert logout_response.status_code == 200
    assert logout_response.json()['status'] == 'ok'

    me_response = anonymous_client.get('/api/v1/auth/me')
    assert me_response.status_code == 401
    assert me_response.json()['detail'] == 'Authentication required'


def test_login_rejects_invalid_password(anonymous_client: TestClient):
    response = login(anonymous_client, 'admin', 'wrong-password')
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid username or password'


def test_protected_endpoints_require_authentication(anonymous_client: TestClient):
    response = anonymous_client.get('/api/v1/assets')
    assert response.status_code == 401
    assert response.json()['detail'] == 'Authentication required'


def test_admin_can_create_and_update_users(client: TestClient):
    create_response = client.post(
        '/api/v1/users',
        json={
            'username': 'operator1',
            'display_name': 'Operator One',
            'email': 'operator1@local.labos',
            'password': 'operatorpass',
            'role': 'operator',
            'is_active': True,
            'note': 'Created in auth test',
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created['username'] == 'operator1'
    assert created['role'] == 'operator'

    update_response = client.put(
        f"/api/v1/users/{created['id']}",
        json={
            'username': 'operator1',
            'display_name': 'Operator Prime',
            'email': 'operator.prime@local.labos',
            'role': 'viewer',
            'is_active': True,
            'note': 'Promoted to read-only',
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated['display_name'] == 'Operator Prime'
    assert updated['role'] == 'viewer'

    password_response = client.patch(
        f"/api/v1/users/{created['id']}/password",
        json={'password': 'viewerpass'},
    )
    assert password_response.status_code == 200

    role_response = client.patch(
        f"/api/v1/users/{created['id']}/role",
        json={'role': 'operator'},
    )
    assert role_response.status_code == 200
    assert role_response.json()['role'] == 'operator'


def test_viewer_cannot_write_operational_resources(client: TestClient, anonymous_client: TestClient):
    create_user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'viewer1',
            'display_name': 'Viewer One',
            'email': 'viewer1@local.labos',
            'password': 'viewerpass',
            'role': 'viewer',
            'is_active': True,
            'note': None,
        },
    )
    assert create_user_response.status_code == 201

    login_response = login(anonymous_client, 'viewer1', 'viewerpass')
    assert login_response.status_code == 200

    list_response = anonymous_client.get('/api/v1/inventory')
    assert list_response.status_code == 200

    create_response = anonymous_client.post(
        '/api/v1/inventory',
        json={
            'name': 'Viewer Block Test',
            'category': 'consumable',
            'status': 'available',
            'quantity': 1,
            'unit': 'pcs',
            'min_quantity': 0,
            'location': 'Viewer Shelf',
            'zone': 'Zone Test',
            'supplier': None,
            'sku': None,
            'notes': None,
            'asset_id': None,
            'wiki_ref': None,
            'last_restocked_at': None,
            'expiry_date': None,
        },
    )
    assert create_response.status_code == 403
    assert create_response.json()['detail'] == 'Operator role required'


def test_viewer_cannot_access_user_management(client: TestClient, anonymous_client: TestClient):
    create_user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'viewer2',
            'display_name': 'Viewer Two',
            'email': 'viewer2@local.labos',
            'password': 'viewerpass',
            'role': 'viewer',
            'is_active': True,
            'note': None,
        },
    )
    assert create_user_response.status_code == 201

    login_response = login(anonymous_client, 'viewer2', 'viewerpass')
    assert login_response.status_code == 200

    response = anonymous_client.get('/api/v1/users')
    assert response.status_code == 403
    assert response.json()['detail'] == 'Admin role required'


def test_operator_can_write_operational_resources(client: TestClient, anonymous_client: TestClient):
    create_user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'operator2',
            'display_name': 'Operator Two',
            'email': 'operator2@local.labos',
            'password': 'operatorpass',
            'role': 'operator',
            'is_active': True,
            'note': None,
        },
    )
    assert create_user_response.status_code == 201

    login_response = login(anonymous_client, 'operator2', 'operatorpass')
    assert login_response.status_code == 200

    create_response = anonymous_client.post(
        '/api/v1/inventory',
        json={
            'name': 'Operator Created Item',
            'category': 'consumable',
            'status': 'available',
            'quantity': 5,
            'unit': 'pcs',
            'min_quantity': 2,
            'location': 'Operator Shelf',
            'zone': 'Zone Ops',
            'supplier': None,
            'sku': None,
            'notes': 'Created by operator',
            'asset_id': None,
            'wiki_ref': None,
            'last_restocked_at': None,
            'expiry_date': None,
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()['name'] == 'Operator Created Item'


def test_inactive_user_cannot_log_in(client: TestClient, anonymous_client: TestClient):
    create_user_response = client.post(
        '/api/v1/users',
        json={
            'username': 'inactive1',
            'display_name': 'Inactive One',
            'email': 'inactive1@local.labos',
            'password': 'inactivepass',
            'role': 'viewer',
            'is_active': True,
            'note': None,
        },
    )
    assert create_user_response.status_code == 201
    created = create_user_response.json()

    deactivate_response = client.patch(
        f"/api/v1/users/{created['id']}/active",
        json={'is_active': False},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()['is_active'] is False

    login_response = login(anonymous_client, 'inactive1', 'inactivepass')
    assert login_response.status_code == 403
    assert login_response.json()['detail'] == 'User account is inactive'
