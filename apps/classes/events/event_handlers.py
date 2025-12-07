from django.db.models import Q, F
from apps.classes.models import Classes
from apps.classes.selectors.selectors import get_class_by_id
from apps.core.email_service import send_html_email
from apps.classes.events.events import RescheduleClassEvent, DeletedClassEvent
from zoneinfo import ZoneInfo
from django.utils import timezone


def handle_class_rescheduled_event(event: RescheduleClassEvent):
    cls = Classes.objects.select_related("instructor", "parent_class").get(id=event.class_id)
    root = cls.parent_class or cls

    if event.update_series:
        affected_classes = Classes.objects.filter(Q(parent_class=root) | Q(id=root.id))
    else:
        affected_classes = [cls]

    emails = set()
    for c in affected_classes:
        emails.update(c.bookings.values_list("client__email", flat=True))
    if cls.instructor and cls.instructor.email:
        emails.add(cls.instructor.email)

    if not emails:
        return

    if event.recurrence_changed:
        subject = "Class schedule updated"
        template_name = "emails/class_removed.html"
        class_date = _format_class_date(cls)
        context = {
            "class_name": cls.title,
            "class_date": class_date,
        }
    else:
        formatted_date = _format_class_date(cls, event.new_date)
        subject = "Your class has been rescheduled"
        template_name = "emails/class_rescheduled.html"
        context = {
            "class_name": cls.title,
            "class_date": formatted_date,
            "instructor_name": getattr(cls.instructor, "name", ""),
        }

    for email in emails:
        send_html_email(
            subject=subject,
            to=email,
            template_name=template_name,
            context=context,
        )


def handle_class_deleted_event(event: DeletedClassEvent):
    cls = get_class_by_id(event.class_id)

    bookings = (
        cls.bookings
        .values(
            email=F("client__email"),
        )
    )


    for b in bookings:
        send_html_email(
            subject=f'Class {cls.title} has been canceled',
            to=b["email"],
            template_name="emails/class_removed.html",
            context={
                "class_name": cls.title,
                "class_date": _format_class_date(cls),
            }
        )


def _format_class_date(cls: Classes, date_value=None):
    target_date = date_value or cls.date
    tz_name = getattr(getattr(cls.instructor, "account", None), "timezone", None)
    tz = ZoneInfo(tz_name) if tz_name else timezone.get_current_timezone()
    localized_date = timezone.localtime(target_date, tz)
    return localized_date.strftime("%A, %B %d at %I:%M %p")