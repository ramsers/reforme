from rest_framework import serializers
from django.utils import timezone


class CreateClassesValidator(serializers.Serializer):
    title = serializers.CharField(required=True, allow_null=False, max_length=45)
    description = serializers.CharField(required=True, allow_null=False)
    size = serializers.CharField(required=True, allow_null=False)
    date = serializers.DateTimeField(required=True, allow_null=False)
    instructor_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class PartialUpdateClassesValidator(serializers.Serializer):
    title = serializers.CharField(required=False, allow_null=True, max_length=45)
    description = serializers.CharField(required=False, allow_null=True, max_length=255)
    size = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    date = serializers.DateTimeField(required=False, allow_null=True)

    def validate_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Date must be in the future.")
        return value

    def validate(self, attrs):
        instructor = self.context.get('instructor')
        class_to_update = self.context.get('class')

        if class_to_update.instructor.id != instructor.id:
            raise serializers.ValidationError("You can only update classes you created.")
        return attrs
