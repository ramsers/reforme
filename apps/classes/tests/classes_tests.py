import pytest
from rest_framework import status
from django.utils import timezone
from model_bakery import baker
from apps.classes.models import Classes
from apps.classes.value_objects import ClassRecurrenceType
from conftest import (admin_client)
from django.db.models import Q
import pytest
from apps.classes.services.class_update_services import regenerate_future_classes


pytestmark = pytest.mark.django_db

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

    parent_time = (parent.date.hour, parent.date.minute)
    for child in children:
        assert (child.date.hour, child.date.minute) == parent_time

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
        recurrence_days=[0, 2],
    )
    regenerate_future_classes(root_class=parent_class, starting_from=parent_class)

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

    parent_time = (parent_class.date.hour, parent_class.date.minute)
    for c in new_children:
        assert (c.date.hour, c.date.minute) == parent_time


def test_delete_child_class_removes_future_classes_successfully(admin_client, instructor_user):
    admin, _ = admin_client

    start_date = timezone.now() + timezone.timedelta(days=1)
    payload = {
        "title": "Progressive Pilates",
        "description": "Weekly class series for deletion cascade test.",
        "size": 10,
        "date": start_date.isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.WEEKLY,
        "recurrence_days": [0, 2],
    }

    create_response = admin.post("/classes", payload, format="json")
    assert create_response.status_code == 201, create_response.data

    parent_class = Classes.objects.get(id=create_response.data["id"])
    children_before = list(parent_class.child_classes.order_by("date"))
    assert len(children_before) > 4

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


def test_edit_single_occurrence_updates_only_that_instance(admin_client, instructor_user):
    admin, _ = admin_client
    start_date = timezone.now() + timezone.timedelta(days=1)
    recurrence_days = sorted({start_date.weekday(), (start_date.weekday() + 2) % 7})

    parent_class = baker.make(
        Classes,
        title="Weekly Flow",
        description="Series",
        size=10,
        date=start_date,
        instructor=instructor_user,
        recurrence_type=ClassRecurrenceType.WEEKLY,
        recurrence_days=recurrence_days,
    )

    regenerate_future_classes(root_class=parent_class, starting_from=parent_class)
    target_child = parent_class.child_classes.order_by("date").first()
    assert target_child is not None

    sibling_snapshot = {
        c.id: c.date
        for c in parent_class.child_classes.exclude(id=target_child.id)
    }

    new_date = target_child.date + timezone.timedelta(days=1)
    payload = {
        "title": "Updated Single Occurrence",
        "date": new_date.isoformat(),
    }

    response = admin.patch(f"{classes_endpoint}/{target_child.id}", payload, format="json")
    assert response.status_code == status.HTTP_200_OK, response.data

    target_child.refresh_from_db()
    parent_class.refresh_from_db()

    assert target_child.title == payload["title"]
    assert target_child.date == new_date

    for sid, sdate in sibling_snapshot.items():
        sibling = Classes.objects.get(id=sid)
        assert sibling.date == sdate

    assert parent_class.title == "Weekly Flow"


def test_update_series_recurrence_from_child_regenerates_future_instances(admin_client, instructor_user):
    admin, _ = admin_client

    start_date = timezone.now() + timezone.timedelta(days=1)
    recurrence_days = sorted({start_date.weekday(), (start_date.weekday() + 2) % 7})

    parent_class = baker.make(
        Classes,
        title="Weekly Flow",
        description="Series",
        size=10,
        date=start_date,
        instructor=instructor_user,
        recurrence_type=ClassRecurrenceType.WEEKLY,
        recurrence_days=recurrence_days,
    )

    regenerate_future_classes(root_class=parent_class, starting_from=parent_class)

    children = list(parent_class.child_classes.order_by("date"))
    assert len(children) >= 2

    target_child = children[0]
    old_future_ids = {c.id for c in children if c.date > target_child.date}

    new_days = sorted({(day + 1) % 7 for day in recurrence_days})
    payload = {
        "recurrence_type": ClassRecurrenceType.WEEKLY,
        "recurrence_days": new_days,
        "title": "Updated Series Title",
        "update_series": True,
    }

    response = admin.patch(f"{classes_endpoint}/{target_child.id}", payload, format="json")
    assert response.status_code == status.HTTP_200_OK, response.data

    parent_class.refresh_from_db()
    assert parent_class.recurrence_days == new_days

    updated_future = list(parent_class.child_classes.filter(date__gt=target_child.date))
    assert updated_future
    assert not old_future_ids & {c.id for c in updated_future}

    assert all(c.date.weekday() in new_days for c in updated_future)

    affected = parent_class.child_classes.filter(date__gte=target_child.date)
    assert affected.exists()
    assert all(c.title == "Updated Series Title" for c in affected)


def test_update_series_time_only_shifts_future_occurrences(admin_client, instructor_user):
    admin, _ = admin_client

    start_date = (timezone.now() + timezone.timedelta(days=1)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    recurrence_days = [start_date.weekday()]

    parent_class = baker.make(
        Classes,
        title="Weekly Flow",
        description="Series",
        size=10,
        date=start_date,
        instructor=instructor_user,
        recurrence_type=ClassRecurrenceType.WEEKLY,
        recurrence_days=recurrence_days,
    )

    regenerate_future_classes(root_class=parent_class, starting_from=parent_class)

    original_child_dates = {
        c.id: c.date for c in parent_class.child_classes.order_by("date")
    }
    assert original_child_dates

    new_datetime = parent_class.date.replace(hour=11, minute=30)
    payload = {
        "date": new_datetime.isoformat(),
        "update_series": True,
    }

    response = admin.patch(f"{classes_endpoint}/{parent_class.id}", payload, format="json")
    assert response.status_code == status.HTTP_200_OK, response.data

    parent_class.refresh_from_db()

    assert parent_class.date.hour == 11
    assert parent_class.date.minute == 30

    updated_children = parent_class.child_classes.order_by("date")
    assert updated_children.exists()

    for child in updated_children:
        original_date = original_child_dates[child.id]
        assert child.date.date() == original_date.date()

        assert child.date.hour == 11
        assert child.date.minute == 30


def test_create_weekly_class_requires_recurrence_days(admin_client, instructor_user):
    admin, _ = admin_client
    payload = {
        "title": "Weekly Pilates",
        "description": "Every Monday and Wednesday morning.",
        "size": 10,
        "date": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.WEEKLY,
    }

    response = admin.post(classes_endpoint, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recurrence_days" in response.data
    assert response.data["recurrence_days"][0] == "This field is required when recurrence_type is WEEKLY."


def test_create_non_weekly_class_rejects_recurrence_days(admin_client, instructor_user):
    admin, _ = admin_client
    payload = {
        "title": "Monthly Pilates",
        "description": "Monthly with bad days",
        "size": 10,
        "date": (timezone.now() + timezone.timedelta(days=3)).isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.MONTHLY,
        "recurrence_days": [0, 2],
    }

    response = admin.post(classes_endpoint, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "recurrence_days" in response.data
    assert response.data["recurrence_days"][0] == "This field is only allowed when recurrence_type is WEEKLY."


def test_children_inherit_parent_recurrence(admin_client, instructor_user):
    admin, _ = admin_client
    start_date = timezone.now() + timezone.timedelta(days=1)

    payload = {
        "title": "Weekly Pilates",
        "description": "Every Monday and Wednesday morning.",
        "size": 10,
        "date": start_date.isoformat(),
        "instructor_id": str(instructor_user.id),
        "recurrence_type": ClassRecurrenceType.WEEKLY,
        "recurrence_days": [0, 2],
    }

    res = admin.post(classes_endpoint, payload, format="json")
    assert res.status_code == status.HTTP_201_CREATED

    parent_id = res.data["id"]

    parent_res = admin.get(f"{classes_endpoint}/{parent_id}")
    parent = parent_res.data

    assert parent["recurrence_type"] == ClassRecurrenceType.WEEKLY
    assert parent["recurrence_days"] == [0, 2]

    children_res = admin.get(f"{classes_endpoint}?parent_class_id={parent_id}")
    children = children_res.data["results"]

    assert len(children) > 0

    for child in children:
        assert child["recurrence_type"] == parent["recurrence_type"]
        assert child["recurrence_days"] == parent["recurrence_days"]

