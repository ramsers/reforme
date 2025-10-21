from apps.classes.events.events import RescheduleClassEvent
from apps.classes.models import Classes

def handle_class_rescheduled_event(event: RescheduleClassEvent):
    cls = Classes.objects.select_related("instructor", "parent_class").get(id=event.class_id)
    root = cls.parent_class or cls

    # Determine affected classes
    if event.update_series:
        affected_classes = Classes.objects.filter(Q(parent_class=root) | Q(id=root.id))
        subject = "Class schedule updated"
        message = (
            "Unfortunately, this class is no longer continuing at the previous schedule.\n\n"
            "Please check the website for the new class schedule:\n"
            "https://yourwebsite.com/schedule"
        )
    else:
        affected_classes = [cls]
        formatted_date = event.new_date.strftime("%A, %B %d at %I:%M %p")
        subject = f"Your class '{cls.title}' has been updated"
        message = f"Your class has been updated to {formatted_date}."

    emails = set()
    for c in affected_classes:
        emails.update(c.bookings.values_list("client__email", flat=True))
    if cls.instructor and cls.instructor.email:
        emails.add(cls.instructor.email)

    if not emails:
        return

    print('EMAILS ================', emails)

    # for email in emails:
    #     send_mail(
    #         subject=subject,
    #         message=message,
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         recipient_list=[email],
    #         fail_silently=True,
    #     )

