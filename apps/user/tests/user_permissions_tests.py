from conftest import admin_client, instructor_client, client_client
from apps.user.value_objects import Role
from rest_framework import status

users_endpoint = "/users"
pytestmark = pytest.mark.django_db


def test_user_create_permissions(admin_client, instructor_client, client_client):
    new_user_payload = {
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "name": "New User",
        "role": Role.CLIENT,
    }

    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    admin_response = admin.post(users_endpoint, new_user_payload, format="json")
    instructor_response = instructor.post(users_endpoint, new_user_payload, format="json")
    client_response = client.post(users_endpoint, new_user_payload, format="json")

    assert admin_response.status_code == status.HTTP_201_CREATED
    assert instructor_response.status_code == status.HTTP_400_BAD_REQUEST
    assert client_response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_update_permissions(admin_client, instructor_client, client_client):
    payload = {
        "email": "update@example.com",
        "password": "updatedPassword!",
        "name": "New User",
        "role": Role.CLIENT,
    }

    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    admin_response = admin.patch(f"{users_endpoint}/{client_user.id}", payload, format="json")
    instructor_response = instructor.patch(f"{users_endpoint}/{client_user.id}", payload, format="json")
    client_response = client.patch(f"{users_endpoint}/{client_user.id}", payload, format="json")

    assert admin_response.status_code == status.HTTP_200_OK
    assert instructor_response.status_code == status.HTTP_400_BAD_REQUEST
    assert client_response.status_code == status.HTTP_200_OK


def test_get_all_instructors(admin_client, instructor_client, client_client):
    instructors_endpoint = f"{users_endpoint}/all-instructors"

    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    admin_response = admin.get(instructors_endpoint)
    instructor_response = instructor.get(instructors_endpoint)
    client_response = client.get(instructors_endpoint)

    assert admin_response.status_code == status.HTTP_200_OK
    assert instructor_response.status_code == status.HTTP_403_FORBIDDEN
    assert client_response.status_code == status.HTTP_403_FORBIDDEN

def test_get_all_clients(admin_client, instructor_client, client_client):
    instructors_endpoint = f"{users_endpoint}/all-clients"

    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    admin_response = admin.get(instructors_endpoint)
    instructor_response = instructor.get(instructors_endpoint)
    client_response = client.get(instructors_endpoint)

    assert admin_response.status_code == status.HTTP_200_OK
    assert instructor_response.status_code == status.HTTP_403_FORBIDDEN
    assert client_response.status_code == status.HTTP_403_FORBIDDEN



