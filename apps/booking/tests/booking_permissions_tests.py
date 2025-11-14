from conftest import admin_client, instructor_client, client_client, sample_class, sample_booking
from rest_framework import status
from apps.booking.models import Booking

bookings_endpoint = "/bookings"

def test_create_booking_permissions(admin_client, instructor_client, client_client, sample_class):
    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    payload = {"class_id": str(sample_class.id), "client_id": str(client_user.id)}

    admin_response = admin.post(bookings_endpoint, payload, format="json")
    instructor_response = instructor.post(bookings_endpoint, payload, format="json")
    client_response = client.post(bookings_endpoint, payload, format="json")

    assert admin_response.status_code == status.HTTP_201_CREATED
    assert instructor_response.status_code == status.HTTP_400_BAD_REQUEST
    assert client_response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_booking_permissions(admin_client, instructor_client, client_client, sample_booking, sample_class):
    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    client_booking = Booking.objects.create(client=client_user, booked_class=sample_class)
    instructor_booking = Booking.objects.create(client=client_user, booked_class=sample_class)
    admin_booking = Booking.objects.create(client=client_user, booked_class=sample_class)

    resp_client = client.delete(f"/bookings/{client_booking.id}/delete")
    assert resp_client.status_code == status.HTTP_204_NO_CONTENT

    resp_admin = admin.delete(f"/bookings/{admin_booking.id}/delete")
    assert resp_admin.status_code == status.HTTP_204_NO_CONTENT

    resp_instructor = instructor.delete(f"/bookings/{instructor_booking.id}/delete")
    assert resp_instructor.status_code == status.HTTP_400_BAD_REQUEST
