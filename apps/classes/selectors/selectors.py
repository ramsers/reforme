from apps.classes.models import Classes


def get_class_by_id(id: str):
    try:
        classes = Classes.objects.get(id=id)
    except Classes.DoesNotExist:
        return None
    return classes