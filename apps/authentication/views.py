from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from apps.user.models import User
from rest_framework_simplejwt.tokens import RefreshToken



class SignUpAPI(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Create user (this will hash the password automatically)
            user = User.objects.create(
                email=email,
                password=password,
                name=name or ""
            )

        # Create JWT for the new user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                },
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )
