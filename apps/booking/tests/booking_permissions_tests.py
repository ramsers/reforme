from conftest import admin_client, instructor_client, client_client, sample_class, sample_booking
from rest_framework import status

bookings_endpoint = "/bookings"

def test_booking_create_permissions(admin_client, instructor_client, client_client, sample_class):
    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    payload = {"class_id": str(sample_class.id), "client_id": str(client_user.id)}

    admin_response = admin.post(bookings_endpoint, payload, format="json")
    instructor_response = instructor.post(bookings_endpoint, payload, format="json")
    client_response = client.post(bookings_endpoint, payload, format="json")

    print("Admin response:", admin_response.data, flush=True)
    print("Instructor response:", instructor_response.status_code, flush=True)
    print("Client response:", client_response.status_code, flush=True)

    assert admin_response.status_code == status.HTTP_201_CREATED
    assert instructor_response.status_code == status.HTTP_400_BAD_REQUEST
    assert client_response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(client_response.data['non_field_errors'][0]) == 'already_booked'


def test_booking_delete_permissions(admin_client, instructor_client, client_client, sample_booking):
    delete_endpoint = f"/bookings/{sample_booking.id}/delete"
    admin, admin_user = admin_client
    instructor, instructor_user = instructor_client
    client, client_user = client_client

    admin_response = admin.delete(delete_endpoint)
    instructor_response = instructor.delete(delete_endpoint)
    client_response = client.delete(delete_endpoint)

    print("Admin response:", admin_response.data, flush=True)
    print("Instructor response:", instructor_response.status_code, flush=True)
    print("Client response:", client_response.status_code, flush=True)

    assert admin_response.status_code == status.HTTP_201_CREATED
    assert instructor_response.status_code == status.HTTP_400_BAD_REQUEST
    assert client_response.status_code == status.HTTP_400_BAD_REQUEST
    assert str(client_response.data['non_field_errors'][0]) == 'already_booked'
