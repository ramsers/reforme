import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db(transaction=True)


def test_create_purchase_intent_returns_url_and_secret(client_client, monkeypatch):
    client, _ = client_client
    commands = []
    checkout_url = "https://stripe.test/session"
    client_secret = "pi_secret_123"

    def fake_handle(command):
        commands.append(command)
        return checkout_url if command.is_subscription else client_secret

    monkeypatch.setattr("apps.payment.views.payment_command_bus.handle", fake_handle)

    url = reverse("create-purchase-intent")

    subscription_payload = {
        "price_id": "price_subscription",
        "product_name": "Monthly Unlimited",
        "is_subscription": True,
        "price_amount": 100,
        "currency": "cad",
        "duration_days": 30,
        "redirect_url": "https://example.com/redirect",
    }

    subscription_response = client.post(url, data=subscription_payload, format="json")

    one_time_payload = {
        "price_id": "price_onetime",
        "product_name": "Day Pass",
        "is_subscription": False,
        "price_amount": 25,
        "currency": "cad",
        "duration_days": 1,
    }

    one_time_response = client.post(url, data=one_time_payload, format="json")

    assert subscription_response.status_code == 200
    assert subscription_response.json() == checkout_url

    assert one_time_response.status_code == 200
    assert one_time_response.json() == client_secret

    assert len(commands) == 2
    assert commands[0].redirect_url == subscription_payload["redirect_url"]
    assert commands[1].redirect_url is None


def test_create_purchase_intent_with_invalid_redirect_url(client_client, monkeypatch):
    client, _ = client_client

    handle_called = False

    def fake_handle(command):
        nonlocal handle_called
        handle_called = True
        return "should-not-be-called"

    monkeypatch.setattr("apps.payment.views.payment_command_bus.handle", fake_handle)

    url = reverse("create-purchase-intent")
    payload = {
        "price_id": "price_bad_url",
        "product_name": "Monthly",
        "is_subscription": True,
        "price_amount": 100,
        "currency": "cad",
        "duration_days": 30,
        "redirect_url": "not-a-valid-url",
    }

    response = client.post(url, data=payload, format="json")

    assert response.status_code == 400
    assert "redirect_url" in response.data
    assert handle_called is False