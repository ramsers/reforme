from rest_framework import serializers
from apps.classes.models import Classes
from apps.user.serializers import UserSerializer
from apps.user.models import User


class ClassesSerializer(serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()

    def get_instructor(self, obj):
        instructor = obj.instructor
        return UserSerializer(instructor).data

    class Meta:
        model = Classes
        fields = "__all__"
