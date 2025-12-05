from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random

from apps.user.models import User, Role, Account
from apps.classes.models import Classes, ClassRecurrenceType
from apps.booking.models import Booking
from apps.payment.models import PassPurchase
from apps.classes.services.class_update_services import build_recurring_schedule


class Command(BaseCommand):
    help = "Seed the database with demo users, classes, bookings, and passes."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Clearing previous seed data..."))

        Classes.objects.filter(title__startswith="[DEMO]").delete()
        PassPurchase.objects.filter(pass_name__startswith="[DEMO]").delete()

        self.stdout.write(self.style.SUCCESS("Old seed data removed."))

        self.stdout.write(self.style.WARNING("Creating users..."))
        admin = self._create_user(
            email="reforme_admin@gmail.com",
            name="Reforme Admin",
            role=Role.ADMIN,
            password="admin123!",
        )

        instructors_data = [
            ("julia.thompson@reforme.com", "Julia Thompson"),
            ("marco.silvera@reforme.com", "Marco Silvera"),
        ]

        instructors = [
            self._create_user(email, name, Role.INSTRUCTOR, "password123!")
            for email, name in instructors_data
        ]

        clients_data = [
            ("john.doe@gmail.com", "John Doe"),
            ("emma.watson@gmail.com", "Emma Watson"),
            ("liam.bennett@gmail.com", "Liam Bennett"),
            ("sophia.mendez@gmail.com", "Sophia Mendez"),
            ("noah.anderson@gmail.com", "Noah Anderson"),
            ("mia.hernandez@gmail.com", "Mia Hernandez"),
            ("oliver.patel@gmail.com", "Oliver Patel"),
        ]

        clients = [
            self._create_user(email, name, Role.CLIENT, "password123!")
            for email, name in clients_data
        ]

        self.stdout.write(self.style.SUCCESS("Demo users created."))

        self.stdout.write(self.style.WARNING("Creating recurring demo classes..."))

        series_definitions = [
            {
                "title": "Morning Pilates",
                "description": "Gentle morning Pilates for all levels.",
                "hour": 9,
                "recurrence_type": ClassRecurrenceType.WEEKLY,
                "recurrence_days": [0, 2],
                "weeks_ahead": 4,
            },
            {
                "title": "Evening Strength",
                "description": "Full body strength conditioning.",
                "hour": 18,
                "recurrence_type": ClassRecurrenceType.WEEKLY,
                "recurrence_days": [1, 3],
                "weeks_ahead": 4,
            },
        ]

        all_classes = []

        for idx, series in enumerate(series_definitions):
            instructor = instructors[idx % len(instructors)]

            parent_date = self._next_recurrence_date(
                hour=series["hour"], recurrence_days=series["recurrence_days"]
            )

            parent = Classes.objects.create(
                title=series["title"],
                description=series["description"],
                size=12,
                length=45,
                date=parent_date,
                instructor=instructor,
                recurrence_type=series["recurrence_type"],
                recurrence_days=series["recurrence_days"],
                parent_class=None,
            )
            all_classes.append(parent)

            children = build_recurring_schedule(
                root_class=parent,
                start_date=parent.date,
                max_instances=series["weeks_ahead"] * len(series["recurrence_days"])
            )

            Classes.objects.bulk_create(children)
            all_classes.extend(children)

        self.stdout.write(self.style.SUCCESS(f"Created {len(all_classes)} demo classes (parent + children)."))

        self.stdout.write(self.style.WARNING("Creating demo pass purchases..."))
        self._create_passes_for_clients(clients)

        self.stdout.write(self.style.WARNING("Creating demo bookings..."))
        self._create_bookings_for_classes(all_classes, clients)

        self.stdout.write(self.style.SUCCESS("Demo data seeding complete."))

    def _next_recurrence_date(self, hour: int, recurrence_days: list[int]):
        """Return the next datetime that matches the recurrence days and hour."""

        now = timezone.localtime()

        for offset in range(0, 7):
            candidate = now + timedelta(days=offset)
            candidate_dt = candidate.replace(
                hour=hour, minute=0, second=0, microsecond=0
            )

            if candidate.weekday() in recurrence_days and candidate_dt > now:
                return candidate_dt

        next_week = now + timedelta(days=7)
        return next_week.replace(hour=hour, minute=0, second=0, microsecond=0)

    def _create_user(self, email: str, name: str, role: str, password: str) -> User:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                "role": role,
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Created user: {email} ({role})"))
        else:
            self.stdout.write(f"User already exists: {email} ({role})")

        account, account_created = Account.objects.get_or_create(
            user=user, defaults={"timezone": "EST"}
        )
        if account_created:
            self.stdout.write(
                self.style.SUCCESS(f"Created account for user: {email} ({role})")
            )
        else:
            self.stdout.write(f"Account already exists for user: {email} ({role})")
        return user

    def _create_passes_for_clients(self, clients):
        now = timezone.now()
        for client in clients:
            PassPurchase.objects.create(
                user=client,
                stripe_price_id="price_demo_sub_active",
                pass_name="Monthly Unlimited",
                is_subscription=True,
                start_date=now - timedelta(days=7),
                end_date=now + timedelta(days=23),
                active=True,
            )

            PassPurchase.objects.create(
                user=client,
                stripe_price_id="price_demo_pack_expired",
                pass_name="5-Class Pack",
                is_subscription=False,
                start_date=now - timedelta(days=60),
                end_date=now - timedelta(days=30),
                active=False,
            )

    def _create_bookings_for_classes(self, classes, clients):
        future_classes = [c for c in classes if c.date > timezone.now()]

        for cls in future_classes:
            max_bookings = random.randint(1, max(1, int(cls.size * 0.7)))
            chosen_clients = random.sample(clients, k=min(max_bookings, len(clients)))

            for client in chosen_clients:
                Booking.objects.get_or_create(
                    client=client,
                    booked_class=cls,
                )
