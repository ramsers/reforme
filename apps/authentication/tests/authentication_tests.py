from apps.user.value_objects import Role
import pytest
from rest_framework import status
from model_bakery import baker
from django.contrib.auth import get_user_model
from apps.authentication.models import PasswordResetToken


User = get_user_model()
pytestmark = pytest.mark.django_db
signup_endpoint = "/authentication/sign-up"
login_endpoint = "/authentication/login"
reset_password_endpoint = "/authentication/reset-password"


def test_signup_successfully(api_client):
    payload = {
        "email": "newuser@example.com",
        "password": "Testpass123!",
        "name": "New User",
        "role": Role.CLIENT,
        "timezone": "America/New_York",
    }

    resp = api_client.post(signup_endpoint, payload, format="json")

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert "user" in data
    assert "access" in data and data["access"]
    assert "refresh" in data and data["refresh"]
    user_data = data["user"]
    assert user_data["email"] == payload["email"]
    assert user_data["name"] == payload["name"]
    assert user_data["role"] == payload["role"]
    assert user_data["account"]["timezone"] == payload["timezone"]

    user = User.objects.get(email=payload["email"])
    assert user.account.timezone == payload["timezone"]


def test_signup_missing_email_and_password(api_client):
    payload_no_email = {
        "password": "Testpass123!",
        "name": "No Email",
        "role": Role.CLIENT,
    }
    resp_no_email = api_client.post(signup_endpoint, payload_no_email, format="json")

    assert resp_no_email.status_code == status.HTTP_400_BAD_REQUEST
    assert str(resp_no_email.data['email'][0]) == "This field is required."

    payload_no_password = {
        "email": "no_password@example.com",
        "name": "No Password",
        "role": Role.CLIENT,
    }
    resp_no_password = api_client.post(signup_endpoint, payload_no_password, format="json")

    assert resp_no_password.status_code == status.HTTP_400_BAD_REQUEST
    assert str(resp_no_password.data['password'][0]) == "This field is required."

def test_signup_duplicate_email(api_client):
    url = "/authentication/sign-up"

    existing_user = User.objects.create(
        email="taken@example.com",
        password="ExistingPass123!",
        name="Existing User",
        role=Role.CLIENT,
    )

    payload = {
        "email": existing_user.email,
        "password": "AnotherPass123!",
        "name": "New User",
        "role": Role.CLIENT,
    }

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert str(resp.data['non_field_errors'][0]) == "This email is already in use"

def test_login_successfully(api_client, test_user):
    payload = {
        "email": test_user.email,
        "password": "testpassword!",
    }

    resp = api_client.post(login_endpoint, payload, format="json")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()

    assert "user" in data
    assert "access" in data and data["access"]
    assert "refresh" in data and data["refresh"]

    user_data = data["user"]
    assert user_data["email"] == test_user.email
    assert user_data["name"] == test_user.name

def test_login_missing_email_or_password_should_fail(api_client):
    payload_no_email = {"password": "SomePass123!"}
    resp_no_email = api_client.post(login_endpoint, payload_no_email, format="json")

    assert resp_no_email.status_code == status.HTTP_400_BAD_REQUEST
    assert str(resp_no_email.data['email'][0]) == "This field is required."

    payload_no_password = {"email": "user@example.com"}
    resp_no_password = api_client.post(login_endpoint, payload_no_password, format="json")
    assert resp_no_password.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_no_password.data['password'][0] == "This field is required."

def test_login_invalid_credentials_should_fail(api_client):
    user = User.objects.create(
        email="validuser@example.com",
        password="ValidPass123!",
        name="Valid User",
        role=Role.CLIENT,
    )

    payload_invalid_email = {"email": "doesnotexist@example.com", "password": user.password}
    resp_invalid_email = api_client.post(login_endpoint, payload_invalid_email, format="json")

    assert resp_invalid_email.status_code == status.HTTP_400_BAD_REQUEST
    assert str(resp_invalid_email.data['non_field_errors'][0]) == "User not found"

    payload_wrong_password = {"email": user.email, "password": "WrongPass999!"}
    resp_wrong_password = api_client.post(login_endpoint, payload_wrong_password, format="json")

    assert resp_wrong_password.status_code == status.HTTP_400_BAD_REQUEST
    assert str(resp_wrong_password.data['non_field_errors'][0]) == "Password doesn't match"


def test_forgot_password_successfully(api_client, test_user):
    payload = {"email": test_user.email}

    resp = api_client.post("/authentication/forgot-password", payload, format="json")

    assert resp.status_code == status.HTTP_200_OK


def test_forgot_password_invalid_email_should_fail(api_client):
    payload = {"email": "idontexist@example.com"}

    resp = api_client.post("/authentication/forgot-password", payload, format="json")

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in resp.data
    assert resp.data["email"][0] == "If email exists, a reset link will be sent."


def test_reset_password_successfully(api_client, user_with_reset_token):
    user, token = user_with_reset_token

    payload = {
        "token": token,
        "password": "NewPass123!",
    }

    response = api_client.post(reset_password_endpoint, payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()

    assert user.check_password("NewPass123!")
    assert not PasswordResetToken.objects.filter(token=token).exists()

