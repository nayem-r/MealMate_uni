
from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.home,
        name="home"
    ),
    path(
        "signup/",
        views.signup_user,
        name="signup_user"
    ),
    path(
        "signup/business/",
        views.signup_business,
        name="signup_business"
    ),
    path(
        "signup/success/",
        views.signup_success,
        name="signup_success"
    ),
]
