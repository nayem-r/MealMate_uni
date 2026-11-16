
from django import forms

from .models import MealMateUser


class SignupForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Full name",
            }
        ),
    )

    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Email address",
            }
        ),
    )

    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Phone number (optional)",
            }
        ),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Password",
            }
        ),
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Confirm password",
            }
        ),
    )

    def clean_full_name(self):
        value = self.cleaned_data["full_name"].strip()

        if len(value) < 2:
            raise forms.ValidationError(
                "Please enter a valid name."
            )

        return value

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if MealMateUser.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        cleaned = super().clean()

        password = cleaned.get("password")
        confirm = cleaned.get("confirm_password")

        if password and len(password) < 8:
            self.add_error(
                "password",
                "Password must contain at least 8 characters."
            )

        if password and confirm and password != confirm:
            self.add_error(
                "confirm_password",
                "Passwords do not match."
            )

        return cleaned
