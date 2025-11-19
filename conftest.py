import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.models import Role
from apps.classes.models import Classes
from apps.booking.models import Booking
from django.utils import timezone
from apps.payment.models import PassPurchase
from apps.authentication.models import PasswordResetToken

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


def create_authenticated_client(role: str):
    user = baker.make(User, email=f"{role.lower()}@reforme.com", role=role, name=f"{role.title()} User")
    user.set_password("testpassword123!")
    user.save()

    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    return client, user


@pytest.fixture
def test_user(db):
    user = baker.make(User, email="testuser@example.com")
    user.set_password("testpassword!")
    user.save(update_fields=["password"])
    return user


@pytest.fixture
def instructor_client(db):
    client, user = create_authenticated_client(Role.INSTRUCTOR)
    return client, user


@pytest.fixture
def client_client(db):
    client, user = create_authenticated_client(Role.CLIENT)
    return client, user

@pytest.fixture
def client_client_with_active_purchase(db):
    client, user = create_authenticated_client(Role.CLIENT)

    PassPurchase.objects.create(
        user=user,
        stripe_product_id="prod_active",
        stripe_customer_id="cus_active",
        pass_name="Unlimited Monthly",
        is_subscription=True,
        active=True,
        start_date=timezone.now() - timezone.timedelta(days=3),
        end_date=timezone.now() + timezone.timedelta(days=999),
        is_cancel_requested=False,
    )

    return client, user


@pytest.fixture
def admin_client(db):
    client, user = create_authenticated_client(Role.ADMIN)
    return client, user

@pytest.fixture
def client_user(db):
    return baker.make(User, role=Role.CLIENT, email="client@example.com")


@pytest.fixture
def instructor_user(db):
    return baker.make(User, role=Role.INSTRUCTOR, email="instructor@example.com")


@pytest.fixture
def sample_class(db, instructor_user):
    return baker.make(
        Classes,
        title="Morning Pilates",
        description="A beginner pilates session.",
        instructor=instructor_user,
        date=timezone.now() + timezone.timedelta(days=1),
        size=2
    )


@pytest.fixture
def sample_booking(db, client_user, sample_class):
    return Booking.objects.create(client=client_user, booked_class=sample_class)


@pytest.fixture
def user_with_reset_token(db):
    user = User.objects.create(
        email="reset@example.com",
        name="Reset User",
        role=Role.CLIENT,
    )
    user.set_password("OldPassword123!")
    user.save()

    token = PasswordResetToken.objects.create(
        user=user,
        token=PasswordResetToken.generate_token(),
    )

    return user, token.token

