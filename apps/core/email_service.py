from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import os

def send_html_email(subject: str, to: str, template_name: str, context: dict):
    html_content = render_to_string(template_name, context)
    text_content = f"{context.get('client_name', '')}, please check your booking details."

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=os.environ.get('DEFAULT_FROM_EMAIL'),
        to=[to],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()