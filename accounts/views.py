
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignupForm
from .models import MealMateUser


def create_login_session(request, user):
    request.session.cycle_key()

    request.session["user_id"] = user.id
    request.session["user_name"] = user.full_name
    request.session["user_email"] = user.email
    request.session["user_role"] = user.role


def get_current_user(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    user = MealMateUser.objects.filter(
        id=user_id,
        is_active=True
    ).first()

    if not user:
        request.session.flush()
        return None

    return user


def home(request):
    return render(
        request,
        "index.html",
        {
            "current_user": get_current_user(request)
        }
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
    current_user = get_current_user(request)

    if current_user:
        return redirect("home")

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


def login_user(request):
    current_user = get_current_user(request)

    if current_user:
        return redirect("home")

    form = LoginForm(
        request.POST if request.method == "POST" else None
    )

    if request.method == "POST" and form.is_valid():
        user = MealMateUser.objects.filter(
            email__iexact=form.cleaned_data["email"]
        ).first()

        if user and check_password(
            form.cleaned_data["password"],
            user.password_hash
        ):
            if not user.is_active:
                form.add_error(
                    None,
                    "This account is inactive."
                )
            else:
                create_login_session(
                    request,
                    user
                )

                messages.success(
                    request,
                    "You have signed in successfully."
                )

                return redirect("home")
        else:
            form.add_error(
                None,
                "Incorrect email or password."
            )

    return render(
        request,
        "login.html",
        {
            "form": form
        }
    )


@require_POST
def logout_user(request):
    request.session.flush()

    return redirect("home")
