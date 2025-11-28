import json

import pytest
from django.urls import reverse

from apps.user.models import Role, User
from apps.payment.models import PassPurchase


pytestmark = pytest.mark.django_db

def test_duplicate_checkout_events_are_ignored(api_client, monkeypatch):
    user = User.objects.create(email='duplicate@example.com', name='Client', role=Role.CLIENT)
    user.set_password('testpass123!')
    user.save(update_fields=['password'])

    metadata = {
        'user_id': str(user.id),
        'product_name': 'Unlimited Membership',
        'price_id': 'price_123',
        'product_id': 'prod_123',
        'duration_days': '30',
        'event_id': 'evt_123',
    }

    event_payload = {
        'id': 'evt_stripe',
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'id': 'cs_test',
                'metadata': metadata,
                'subscription': 'sub_123',
                'customer': 'cus_123',
            }
        },
    }

    monkeypatch.setenv('STRIPE_WEBHOOK_SECRET', 'whsec_test')

    def fake_construct_event(payload, header, secret):
        return event_payload

    monkeypatch.setattr(
        'apps.payment.services.webhook_handlers.stripe.Webhook.construct_event',
        fake_construct_event,
    )

    url = reverse('webhook')
    headers = {'HTTP_STRIPE_SIGNATURE': 'sig_test'}

    response_one = api_client.post(url, data=json.dumps({'ping': True}), content_type='application/json', **headers)
    assert response_one.status_code == 200
    assert PassPurchase.objects.count() == 1
    purchase = PassPurchase.objects.first()
    assert purchase.stripe_idempotency_key == 'evt_123'

    response_two = api_client.post(url, data=json.dumps({'ping': True}), content_type='application/json', **headers)
    assert response_two.status_code == 200
    assert PassPurchase.objects.count() == 1