from conftest import admin_client, instructor_client, client_client, sample_class
from rest_framework import status
from django.utils import timezone
from model_bakery import baker
from apps.classes.models import Classes
import pytest


classes_endpoint = "/classes"

pytestmark = pytest.mark.django_db(transaction=True)

def test_create_class_permissions(admin_client, instructor_client, client_client):
    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    payload = {
        "title": "Sunrise Pilates",
        "description": "Gentle morning session.",
        "size": 10,
        "date": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": None,
        "recurrence_days": [],
    }

    admin_response = admin.post(classes_endpoint, payload, format="json")
    instructor_response = instructor.post(classes_endpoint, payload, format="json")
    client_response = client.post(classes_endpoint, payload, format="json")

    assert admin_response.status_code == status.HTTP_201_CREATED
    assert instructor_response.status_code == status.HTTP_403_FORBIDDEN
    assert client_response.status_code == status.HTTP_403_FORBIDDEN



def test_partial_update_class_permissions(admin_client, instructor_client, client_client, sample_class):
    edit_class_endpoint = f"{classes_endpoint}/{sample_class.id}"

    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    payload = {"title": "Updated Title", "size": 12}

    admin_response = admin.patch(edit_class_endpoint, payload, format="json")
    instructor_response = instructor.patch(edit_class_endpoint, payload, format="json")
    client_response = client.patch(edit_class_endpoint, payload, format="json")

    assert admin_response.status_code == status.HTTP_200_OK
    assert instructor_response.status_code == status.HTTP_403_FORBIDDEN
    assert client_response.status_code == status.HTTP_403_FORBIDDEN



def test_delete_class_permissions(admin_client, instructor_client, client_client):
    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    admin_class = baker.make(
        Classes,
        title="Admin Class",
        instructor=instructor_user,
        date=timezone.now() + timezone.timedelta(days=1),
        size=10,
    )

    instructor_class = baker.make(
        Classes,
        title="Instructor Class",
        instructor=instructor_user,
        date=timezone.now() + timezone.timedelta(days=1),
        size=10,
    )

    client_class = baker.make(
        Classes,
        title="Client Class",
        instructor=instructor_user,
        date=timezone.now() + timezone.timedelta(days=1),
        size=10,
    )

    admin_response = admin.delete(f"{classes_endpoint}/{admin_class.id}/delete")
    instructor_response = instructor.delete(f"{classes_endpoint}/{instructor_class.id}/delete")
    client_response = client.delete(f"{classes_endpoint}/{client_class.id}/delete")

    print("Admin response:", admin_response.status_code, flush=True)
    print("Instructor response:", instructor_response.status_code, flush=True)
    print("Client response:", client_response.status_code, flush=True)

    assert admin_response.status_code == status.HTTP_204_NO_CONTENT
    assert instructor_response.status_code == status.HTTP_403_FORBIDDEN
    assert client_response.status_code == status.HTTP_403_FORBIDDEN
