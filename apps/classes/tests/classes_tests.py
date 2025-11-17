import pytest
from rest_framework import status
from django.utils import timezone
from model_bakery import baker
from apps.classes.models import Classes
from apps.classes.value_objects import ClassRecurrenceType
from conftest import (admin_client)
from django.db.models import Q
import pytest
from apps.classes.services.class_update_services import generate_recurring_classes


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

    assert children.exists()

    weekdays = [c.date.weekday() for c in children]
    assert all(day in [0, 2] for day in weekdays)


def test_create_monthly_recurring_classes_successfully(admin_client, instructor_user):
    admin, _ = admin_client
    start_date = timezone.now() + timezone.timedelta(days=3)

    payload = {
        "title": "Monthly Pilates",
        "description": "A monthly Pilates class for members.",
        "size": 12,
        "date": start_date.isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.MONTHLY,
    }

    response = admin.post(classes_endpoint, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data

    parent = Classes.objects.get(id=response.data["id"])
    children = parent.child_classes.all()

    assert parent.recurrence_type == ClassRecurrenceType.MONTHLY

    assert children.exists()

    assert all(c.date > parent.date for c in children)
    parent_day = parent.date.day
    child_days = [c.date.day for c in children]
    assert all(day == parent_day for day in child_days)


def test_create_yearly_recurring_classes_successfully(admin_client, instructor_user):
    admin, _ = admin_client
    start_date = timezone.now() + timezone.timedelta(days=5)

    payload = {
        "title": "Annual Pilates Workshop",
        "description": "A special Pilates workshop that happens once per year.",
        "size": 25,
        "date": start_date.isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.YEARLY,
    }

    response = admin.post(classes_endpoint, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data

    parent = Classes.objects.get(id=response.data["id"])
    children = parent.child_classes.all()

    assert parent.recurrence_type == ClassRecurrenceType.YEARLY

    assert children.exists()

    assert all(c.date > parent.date for c in children)

    parent_month, parent_day = parent.date.month, parent.date.day
    for c in children:
        assert (c.date.month, c.date.day) == (parent_month, parent_day)


def test_create_class_missing_required_fields_should_fail(admin_client, instructor_user):
    admin, _ = admin_client

    payload_no_title = {
        "description": "No title class",
        "size": 10,
        "date": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
        "instructor_id": str(instructor_user.id),
    }
    resp_no_title = admin.post(classes_endpoint, payload_no_title, format="json")
    assert resp_no_title.status_code == status.HTTP_400_BAD_REQUEST
    assert "title" in resp_no_title.data
    assert resp_no_title.data["title"][0] == "This field is required."

    payload_no_description = {
        "title": "Missing Description Class",
        "size": 10,
        "date": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
        "instructor_id": str(instructor_user.id),
    }
    resp_no_description = admin.post(classes_endpoint, payload_no_description, format="json")
    assert resp_no_description.status_code == status.HTTP_400_BAD_REQUEST
    assert "description" in resp_no_description.data
    assert resp_no_description.data["description"][0] == "This field is required."

    payload_no_size = {
        "title": "Missing Size Class",
        "description": "Class without size",
        "date": (timezone.now() + timezone.timedelta(days=2)).isoformat(),
        "instructor_id": str(instructor_user.id),
    }
    resp_no_size = admin.post(classes_endpoint, payload_no_size, format="json")
    assert resp_no_size.status_code == status.HTTP_400_BAD_REQUEST
    assert "size" in resp_no_size.data
    assert resp_no_size.data["size"][0] == "This field is required."

    payload_no_date = {
        "title": "Missing Date Class",
        "description": "Class without a date",
        "size": 10,
        "instructor_id": str(instructor_user.id),
    }
    resp_no_date = admin.post(classes_endpoint, payload_no_date, format="json")
    assert resp_no_date.status_code == status.HTTP_400_BAD_REQUEST
    assert "date" in resp_no_date.data
    assert resp_no_date.data["date"][0] == "This field is required."



def test_partial_update_single_class_successfully(admin_client, instructor_user):
    admin, _ = admin_client

    original_date = timezone.now() + timezone.timedelta(days=2)
    class_obj = baker.make(
        Classes,
        title="Original Title",
        description="Original Description",
        date=original_date,
        size=10,
        instructor=instructor_user
    )

    new_date = original_date + timezone.timedelta(days=2)

    payload = {
        "title": "Updated Title",
        "description": "Updated Description",
        "size": 20,
        "date": new_date.isoformat()
    }

    response = admin.patch(f"{classes_endpoint}/{class_obj.id}", payload, format="json")
    assert response.status_code == status.HTTP_200_OK, response.data

    class_obj.refresh_from_db()

    assert class_obj.title == payload["title"]
    assert class_obj.description == payload["description"]
    assert class_obj.size == payload["size"]

    assert class_obj.date == new_date

    assert not class_obj.child_classes.exists()
    assert class_obj.recurrence_type is None
    assert class_obj.recurrence_days is None



def test_partial_update_weekly_class_updates_series_and_regenerates_children(admin_client, instructor_user):
    admin, _ = admin_client

    start_date = timezone.now() + timezone.timedelta(days=1)
    parent_class = baker.make(
        Classes,
        title="Weekly Pilates",
        description="Every Monday and Wednesday morning.",
        size=10,
        date=start_date,
        instructor=instructor_user,
        recurrence_type=ClassRecurrenceType.WEEKLY,
        recurrence_days=[0, 2]
    )

    generate_recurring_classes(parent_class)
    old_children = list(parent_class.child_classes.all())
    assert old_children
    assert all(c.date.weekday() in [0, 2] for c in old_children)

    old_child_ids = {c.id for c in old_children}

    payload = {
        "recurrence_type": ClassRecurrenceType.WEEKLY,
        "recurrence_days": [1, 3],
        "update_series": True
    }

    response = admin.patch(f"{classes_endpoint}/{parent_class.id}", payload, format="json")
    assert response.status_code == status.HTTP_200_OK, response.data

    parent_class.refresh_from_db()
    new_children = list(parent_class.child_classes.all())
    new_child_ids = {c.id for c in new_children}

    assert parent_class.recurrence_type == ClassRecurrenceType.WEEKLY
    assert parent_class.recurrence_days == [1, 3]

    assert not (old_child_ids & new_child_ids)
    assert new_children
    assert all(c.date.weekday() in [1, 3] for c in new_children)
    assert all(c.date > parent_class.date for c in new_children)


def test_delete_child_class_removes_it_and_future_classes(admin_client, instructor_user):
    admin, _ = admin_client

    # 1️⃣ Create a recurring WEEKLY parent class (Mon/Wed)
    start_date = timezone.now() + timezone.timedelta(days=1)
    payload = {
        "title": "Progressive Pilates",
        "description": "Weekly class series for deletion cascade test.",
        "size": 10,
        "date": start_date.isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.WEEKLY,
        "recurrence_days": [0, 2],  # Monday & Wednesday
    }

    create_response = admin.post("/classes", payload, format="json")
    assert create_response.status_code == 201, create_response.data

    parent_class = Classes.objects.get(id=create_response.data["id"])
    children_before = list(parent_class.child_classes.order_by("date"))
    assert len(children_before) > 4, "Expected multiple recurring children before deletion"

    early_child = children_before[1]

    future_classes = [c for c in children_before if c.date > early_child.date]
    assert len(future_classes) > 0

    delete_endpoint = f"/classes/{early_child.id}/delete?delete_series=true"
    delete_response = admin.delete(delete_endpoint)
    assert delete_response.status_code == 204, delete_response.data

    root = parent_class.parent_class or parent_class
    remaining_classes = (
        Classes.objects.filter(
            Q(parent_class=root) | Q(id=root.id)
        )
        .order_by("date")
    )

    assert remaining_classes.count() > 0
    assert not any(c.date >= early_child.date for c in remaining_classes)
