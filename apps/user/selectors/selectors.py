from apps.user.models import User

def get_user_by_email(email: str):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None

    return user


def get_user_by_id(id: str):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return None

    return user