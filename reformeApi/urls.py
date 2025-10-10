"""reformeApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from apps.user.views import UserViewSet
from apps.authentication.views import SignUpAPI, LoginAPI
from apps.classes.views import ClassesViewSet
from apps.booking.views import BookingViewSet
from apps.payment.views import CreatePurchaseIntentApi, ListProductApi


authentication_patterns = [
    path('sign-up', SignUpAPI.as_view(), name="sign-up"),
    path('login', LoginAPI.as_view(), name="login")
]

payment_patterns = [
    path('create-purchase-intent', CreatePurchaseIntentApi.as_view(), name="create-purchase-intent"),
    path('products', ListProductApi.as_view(), name="products"),
]


router = routers.SimpleRouter(trailing_slash=False)
router.register(r"users", UserViewSet, basename="users")
router.register(r"classes", ClassesViewSet, basename="classes")
router.register(r"bookings", BookingViewSet, basename="bookings")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(router.urls)),
    path("authentication/", include(authentication_patterns)),
    path("payment/", include(payment_patterns)),
]
