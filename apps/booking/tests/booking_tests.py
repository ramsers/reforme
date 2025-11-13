from conftest import (client_client, sample_class,
                      sample_booking, client_user, api_client, client_client_with_active_purchase)
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from model_bakery import baker
from apps.classes.models import Classes
import pytest

bookings_endpoint = "/bookings"

pytestmark = pytest.mark.django_db


def test_create_booking_successfully(client_client_with_active_purchase, sample_class):
    client, client_obj = client_client_with_active_purchase

    payload = {
        "class_id": sample_class.id,
        "client_id": client_obj.id,
    }

    response = client.post(bookings_endpoint, payload, format="json")
    data = response.data

    assert "id" in data
    assert "client" in data
    assert "booked_class" in data

    client_data = data["client"]
    assert client_data["email"] == client_obj.email
    assert client_data["name"] == client_obj.name
    assert "created_at" in client_data

    class_data = data["booked_class"]
    assert class_data["id"] == str(sample_class.id)
    assert class_data["title"] == sample_class.title
    assert class_data["description"] == sample_class.description
    assert "instructor" in class_data

    instructor_data = class_data["instructor"]
    assert instructor_data["email"] == sample_class.instructor.email
    assert instructor_data["name"] == sample_class.instructor.name
    assert response.status_code == status.HTTP_201_CREATED


def test_create_booking_without_active_pass_should_fail(client_client, sample_class):
    client, client_obj = client_client

    payload = {
        "class_id": sample_class.id,
        "client_id": client_obj.id,
    }

    response = client.post(bookings_endpoint, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['non_field_errors'][0] == "no_active_purchase"


@pytest.mark.django_db(transaction=True)
def test_double_booking_should_fail(api_client, client_user, sample_class, sample_booking):

    refresh = RefreshToken.for_user(client_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    payload = {
        "class_id": str(sample_class.id),
        "client_id": str(client_user.id),
    }

    response = api_client.post("/bookings", payload, format="json")
    print("SECOND booking =", response.data, flush=True)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['non_field_errors'][0] == "already_booked"


def test_create_booking_with_missing_fields_should_fail(client_client):
    client, client_obj = client_client
    payload_no_client = {"class_id": "f6a2c7f4-0000-0000-0000-000000000000"}
    resp_no_client = client.post(bookings_endpoint, payload_no_client, format="json")

    assert resp_no_client.status_code == status.HTTP_400_BAD_REQUEST
    assert "client_id" in resp_no_client.data
    assert resp_no_client.data["client_id"][0] == "This field is required."

    payload_no_class = {"client_id": str(client_obj.id)}
    resp_no_class = client.post(bookings_endpoint, payload_no_class, format="json")

    assert resp_no_class.status_code == status.HTTP_400_BAD_REQUEST
    assert "class_id" in resp_no_class.data
    assert resp_no_class.data["class_id"][0] == "This field is required."


def test_create_booking_for_past_class_should_fail(client_client, instructor_user):
    client, client_obj = client_client

    past_class = baker.make(
        Classes,
        title="Yesterday Pilates",
        description="Should not be bookable",
        instructor=instructor_user,
        size=5,
        date=timezone.now() - timezone.timedelta(days=1),
    )

    payload = {
        "class_id": str(past_class.id),
        "client_id": str(client_obj.id),
    }

    response = client.post(bookings_endpoint, payload, format="json")
    print("Response (past class):", response.data, flush=True)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['non_field_errors'][0] == "class_in_past"


def test_admin_can_book_client_without_active_purchase(admin_client, client_user, sample_class):
    admin, admin_user = admin_client

    payload = {
        "class_id": str(sample_class.id),
        "client_id": str(client_user.id),
    }

    response = admin.post(bookings_endpoint, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, response.data
