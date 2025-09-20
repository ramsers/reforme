from rest_framework import serializers
from apps.classes.models import Classes
from apps.user.serializers import UserSerializer
from apps.user.models import User
from django.core.exceptions import ObjectDoesNotExist


class ClassesSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()

    def get_instructor(self, obj):
        try:
            return UserSerializer(obj.instructor).data
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = Classes
        fields = "__all__"
