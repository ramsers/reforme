from rest_framework import serializers
from django.utils import timezone
from apps.classes.value_objects import ClassRecurrenceType


class CreateClassesValidator(serializers.Serializer):
    title = serializers.CharField(required=True, allow_null=False, max_length=45)
    description = serializers.CharField(required=True, allow_null=False)
    size = serializers.CharField(required=True, allow_null=False)
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
