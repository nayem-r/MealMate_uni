
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render

from .forms import SignupForm
from .models import MealMateUser


def home(request):
    return render(
        request,
        "index.html"
    )


def signup_user(request):
    return _signup(
        request,
        role="user"
    )


def signup_business(request):
    return _signup(
        request,
        role="business"
    )


def _signup(request, role):
    form = SignupForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        MealMateUser.objects.create(
            full_name=form.cleaned_data["full_name"],
            email=form.cleaned_data["email"],
            phone=form.cleaned_data["phone"] or None,
            password_hash=make_password(
                form.cleaned_data["password"]
            ),
            role=role,
            is_active=True,
        )

        messages.success(
            request,
            "Your MealMate account has been created."
        )

        return redirect("signup_success")

    return render(
        request,
        "signup.html",
        {
            "form": form,
            "business_signup": role == "business",
        }
    )


def signup_success(request):
    return render(
        request,
        "signup_success.html"
    )
