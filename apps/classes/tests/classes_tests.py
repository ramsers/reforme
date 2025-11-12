import pytest
from rest_framework import status
from django.utils import timezone
from model_bakery import baker
from apps.classes.models import Classes
from apps.classes.value_objects import ClassRecurrenceType

pytestmark = pytest.mark.django_db(transaction=True)

classes_endpoint = "/classes"


def test_create_single_class_successfully(admin_client, instructor_user):
    admin, admin_user = admin_client

    payload = {
        "title": "Morning Pilates",
        "description": "A beginner-level session focused on mobility and core strength.",
        "size": 10,
        "date": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
        "instructor_id": str(instructor_user.id),
    }

    response = admin.post(classes_endpoint, payload, format="json")
    data = response.data

    assert response.status_code == status.HTTP_201_CREATED

    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert str(data["instructor"]["id"]) == payload["instructor_id"]
    assert data["recurrence_type"] is None
    assert data["recurrence_days"] == []

    created_class = Classes.objects.get(id=data["id"])
    assert created_class.title == payload["title"]
    assert created_class.description == payload["description"]
    assert created_class.instructor.id == str(instructor_user.id)


def test_create_weekly_recurring_classes_successfully(admin_client, instructor_user):
    admin, _ = admin_client
    start_date = timezone.now() + timezone.timedelta(days=1)

    payload = {
        "title": "Weekly Pilates",
        "description": "Every Monday and Wednesday morning.",
        "size": 10,
        "date": start_date.isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.WEEKLY,
        "recurrence_days": [0, 2]
    }

    response = admin.post(classes_endpoint, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data

    parent = Classes.objects.get(id=response.data["id"])
    children = parent.child_classes.all()

    assert children.exists(), "Expected recurring child classes to be generated"

    weekdays = [c.date.weekday() for c in children]
    assert all(day in [0, 2] for day in weekdays), f"Found non-Mon/Wed classes: {weekdays}"