import datetime as dt

import pytest
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from apps.classes.models import Classes
from apps.classes.tasks import extend_future_classes

pytestmark = pytest.mark.django_db


def test_extend_future_classes_generates_weekly_instances(monkeypatch, instructor_user):
    past_date = timezone.make_aware(dt.datetime(2024, 1, 1, 9, 0, 0))
    monkeypatch.setattr("apps.classes.tasks.timezone.now", lambda: past_date)

    base_class = Classes.objects.create(
        title="Weekly Pilates",
        description="A weekly pilates session.",
        size=10,
        length=60,
        date=past_date,
        instructor=instructor_user,
        recurrence_type="WEEKLY",
    )

    message = extend_future_classes()

    created_classes = Classes.objects.exclude(id=base_class.id)

    expected_dates = []
    next_date = past_date
    cutoff_date = past_date + dt.timedelta(days=90)

    while next_date <= cutoff_date:
        next_date += dt.timedelta(weeks=1)
        expected_dates.append(next_date)

    assert created_classes.count() == len(expected_dates)
    assert set(created_classes.values_list("date", flat=True)) == set(expected_dates)
    assert message == f"Created {len(expected_dates)} new recurring classes"


def test_extend_future_classes_skips_existing_instances(monkeypatch, instructor_user):
    past_date = timezone.make_aware(dt.datetime(2024, 1, 5, 14, 0, 0))
    monkeypatch.setattr("apps.classes.tasks.timezone.now", lambda: past_date)

    base_class = Classes.objects.create(
        title="Monthly Pilates",
        description="A monthly pilates session.",
        size=8,
        length=45,
        date=past_date,
        instructor=instructor_user,
        recurrence_type="MONTHLY",
    )

    created_classes = Classes.objects.filter(title=base_class.title).exclude(
        id=base_class.id
    )

    expected_dates = []
    next_date = past_date
    cutoff_date = past_date + dt.timedelta(days=90)

    while next_date <= cutoff_date:
        next_date += relativedelta(months=1)
        expected_dates.append(next_date)

    first_run_message = extend_future_classes()

    assert created_classes.count() == len(expected_dates)
    assert set(created_classes.values_list("date", flat=True)) == set(expected_dates)
    assert first_run_message == f"Created {len(expected_dates)} new recurring classes"

    second_run_message = extend_future_classes()

    assert Classes.objects.filter(title=base_class.title).count() == len(expected_dates) + 1
    assert second_run_message == "Created 0 new recurring classes"