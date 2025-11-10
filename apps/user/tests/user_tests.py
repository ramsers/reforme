from conftest import admin_client, client_client
from apps.user.value_objects import Role
from rest_framework import status
from apps.user.models import User
from rest_framework import status

users_endpoint = "/users"

def test_create_user_successfully(admin_client):
    payload = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "name": "New User",
        "role": Role.CLIENT,
    }

    admin, admin_user = admin_client

    admin_response = admin.post(users_endpoint, new_user_payload, format="json")

    assert admin_response.status_code == status.HTTP_201_CREATED
    assert admin_response.data["email"] == payload["email"]
    assert admin_response.data["name"] == payload["name"]
    assert admin_response.data["role"] == payload["role"]

def test_create_user_missing_required_fields(admin_client):
    admin, admin_user = admin_client

    payload_no_name = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "role": Role.CLIENT,
    }
    response = admin.post(users_endpoint, payload_no_name, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.data

    payload_no_email = {
        "name": "New User",
        "password": "StrongPass123!",
        "role": Role.CLIENT,
    }
    response = admin.post(users_endpoint, payload_no_email, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data

    payload_no_role = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "StrongPass123!",
    }
    response = admin.post(users_endpoint, payload_no_role, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "role" in response.data

def test_create_user_duplicate_email(admin_client):
    """Ensure validator rejects duplicate emails."""
    admin, admin_user = admin_client

    User.objects.create(
        email="existing@example.com",
        password="pass123",
        name="Existing User",
        role=Role.CLIENT,
    )

    payload = {
        "email": "existing@example.com",
        "password": "StrongPass123!",
        "name": "New User",
        "role": Role.CLIENT,
    }

    response = admin.post(users_endpoint, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "This email is already in use" in str(response.data["email"][0])



def test_update_user_successfully(admin_client, client_client):
    payload = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "name": "New User",
        "role": Role.CLIENT,
    }

    admin, admin_user = admin_client

    admin_response = admin.post(f"{users_endpoint}/{client_client}", payload, format="json")

    assert admin_response.status_code == status.HTTP_201_CREATED
    assert admin_response.data["email"] == new_user_payload["email"]
    assert admin_response.data["name"] == new_user_payload["name"]
    assert admin_response.data["role"] == new_user_payload["role"]



def test_admin_and_self_can_update_user(admin_client, client_client):
    admin, admin_user = admin_client
    client, client_user = client_client

    admin_payload = {
        "id": str(client_user.id),
        "name": "Updated by Admin",
        "email": "updated_by_admin@example.com",
    }

    admin_response = admin.patch(f"{users_endpoint}/{client_user.id}", admin_payload, format="json")

    assert admin_response.status_code == status.HTTP_200_OK, admin_response.data
    assert admin_response.data["name"] == admin_payload["name"]
    assert admin_response.data["email"] == admin_payload["email"]

    self_payload = {
        "id": str(client_user.id),
        "name": "Updated by Self",
        "email": "updated_by_self@example.com",
    }

    self_response = client.patch(f"{users_endpoint}/{client_user.id}", self_payload, format="json")

    assert self_response.status_code == status.HTTP_200_OK, self_response.data
    assert self_response.data["name"] == self_payload["name"]
    assert self_response.data["email"] == self_payload["email"]
