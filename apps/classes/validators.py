from rest_framework import serializers
from django.utils import timezone
from apps.classes.value_objects import ClassRecurrenceType


class CreateClassesValidator(serializers.Serializer):
    title = serializers.CharField(required=True, allow_null=False, max_length=45)
    description = serializers.CharField(required=True, allow_null=False)
    size = serializers.IntegerField(required=True, allow_null=False, min_value=1)
    date = serializers.DateTimeField(required=True, allow_null=False)
    instructor_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    recurrence_type = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=ClassRecurrenceType.choices
    )
    recurrence_days = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=False,
        allow_null=True
    )

    def validate(self, attrs):
        return _validate_recurrence_rules(attrs)


class PartialUpdateClassesValidator(serializers.Serializer):
    title = serializers.CharField(required=False, allow_null=True, max_length=45)
    description = serializers.CharField(required=False, allow_null=True, max_length=255)
    size = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    date = serializers.DateTimeField(required=False, allow_null=True)
    instructor_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    recurrence_type = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=ClassRecurrenceType.choices
    )
    recurrence_days = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=False,
        allow_null=True
    )

    def validate(self, attrs):
        return _validate_recurrence_rules(attrs)


def _validate_recurrence_rules(attrs):
    recurrence_type = attrs.get("recurrence_type")
    recurrence_days = attrs.get("recurrence_days")

    if recurrence_type == ClassRecurrenceType.WEEKLY:
        if recurrence_days in (None, []):
            raise serializers.ValidationError({
                "recurrence_days": "This field is required when recurrence_type is WEEKLY."
            })
    elif recurrence_days is not None:
        raise serializers.ValidationError({
            "recurrence_days": "This field is only allowed when recurrence_type is WEEKLY."
        })

    return attrs
