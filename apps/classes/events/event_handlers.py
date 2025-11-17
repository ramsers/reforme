from django.db.models import Q, F
from apps.classes.models import Classes
from apps.core.email_service import send_html_email
from apps.classes.events.events import RescheduleClassEvent, DeletedClassEvent


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
        context = {
            "class_name": cls.title,
            "message": (
                "Unfortunately, this class is no longer continuing at the previous schedule. "
                "Please check the website for the new class schedule."
            ),
        }
    else:
        formatted_date = event.new_date.strftime("%A, %B %d at %I:%M %p")
        subject = "Your class has been rescheduled"
        template_name = "emails/class_rescheduled.html"
        context = {
            "class_name": cls.title,
            "new_date": formatted_date,
            "message": f"Your class has been updated to {formatted_date}.",
        }

    for email in emails:
        send_html_email(
            subject=subject,
            to=email,
            template_name=template_name,
            context=context,
        )


def handle_class_deleted_event(event: DeletedClassEvent):
    cls = Classes.objects.get(id=event.class_id)

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
                "class_date": cls.date,
            }
        )
