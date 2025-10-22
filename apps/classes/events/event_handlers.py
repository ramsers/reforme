from django.db.models import Q
from apps.classes.models import Classes
from apps.core.email_service import send_html_email  # your HTML mail helper

def handle_class_rescheduled_event(event):
    """
    Send HTML emails to all booked users + instructor when a class changes.
    - If event.update_series is False: notify for this single class (with new date).
    - If event.update_series is True: notify entire series with a generic schedule update.
    """
    cls = Classes.objects.select_related("instructor", "parent_class").get(id=event.class_id)
    root = cls.parent_class or cls

    # Figure out which classes are affected
    if event.update_series:
        affected_classes = Classes.objects.filter(Q(parent_class=root) | Q(id=root.id))
    else:
        affected_classes = [cls]

    # Collect recipients
    emails = set()
    for c in affected_classes:
        emails.update(c.bookings.values_list("client__email", flat=True))
    if cls.instructor and cls.instructor.email:
        emails.add(cls.instructor.email)

    if not emails:
        return

    # Build message
    if event.update_series:
        subject = "Class schedule updated"
        template_name = "emails/class_recurrence_changed.html"
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

    # Send to all
    for email in emails:
        send_html_email(
            subject=subject,
            to=email,
            template_name=template_name,
            context=context,
        )
