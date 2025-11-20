import json

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.payment.models import PassPurchase


@pytest.mark.django_db
def test_cancel_subscription_flow_successfully(api_client, client_client, monkeypatch):
    client, user = client_client

    purchase = PassPurchase.objects.create(
        user=user,
        stripe_price_id="price_cancel",
        stripe_subscription_id="sub_cancel",
        stripe_customer_id="cus_cancel",
        pass_name="Monthly Unlimited",
        is_subscription=True,
        active=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timezone.timedelta(days=30),
        is_cancel_requested=False,
    )

    subscription_modify_called = {}

    def fake_subscription_modify(subscription_id, **kwargs):
        subscription_modify_called["id"] = subscription_id
        subscription_modify_called["kwargs"] = kwargs
        return {}

    monkeypatch.setattr(
        "apps.payment.commandBus.command_handlers.stripe.Subscription.modify",
        fake_subscription_modify,
    )

    cancel_url = reverse("cancel-subscription", kwargs={"pk": purchase.id})
    cancel_response = client.post(cancel_url)

    purchase.refresh_from_db()

    assert cancel_response.status_code == 200
    assert cancel_response.json() == {"message": "Subscription set to cancel at period end."}
    assert subscription_modify_called["id"] == "sub_cancel"
    assert purchase.is_cancel_requested is True

    event_payload = {
        "id": "evt_cancel",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_cancel",
                "status": "canceled",
                "cancel_at_period_end": False,
            }
        },
    }

    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")

    def fake_construct_event(payload, header, secret):
        return event_payload

    monkeypatch.setattr(
        "apps.payment.services.webhook_handlers.stripe.Webhook.construct_event",
        fake_construct_event,
    )

    webhook_url = reverse("webhook")
    headers = {"HTTP_STRIPE_SIGNATURE": "sig_test"}
    webhook_response = api_client.post(
        webhook_url,
        data=json.dumps({"foo": "bar"}),
        content_type="application/json",
        **headers,
    )

    purchase.refresh_from_db()

    assert webhook_response.status_code == 200
    assert purchase.active is False
    assert purchase.is_cancel_requested is False
    assert purchase.is_active is False


@pytest.mark.django_db
def test_create_purchase_intent_with_invalid_data_should_fail(client_client, monkeypatch):
    client, _ = client_client

    url = reverse("create-purchase-intent")
    payload = {
        "price_id": "price_bad",
        "product_name": "Monthly",
        "is_subscription": True,
        "price_amount": 0,
        "currency": "cad",
        "duration_days": 30,
    }

    response = client.post(url, data=payload, format="json")

    assert response.status_code == 400
    assert "price_amount" in response.data