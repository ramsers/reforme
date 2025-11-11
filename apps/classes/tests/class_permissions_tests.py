from conftest import admin_client, instructor_client, client_client, sample_class, sample_booking
from rest_framework import status

def test_create_class_permissions():
    payload = {}