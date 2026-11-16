
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse

from .models import MealMateUser


class RegistrationTests(TestCase):
    def setUp(self):
        self.valid_data = {
            "full_name": "Test Customer",
            "email": "customer@example.com",
            "phone": "07123456789",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
        }

    def test_user_registration_page(self):
        response = self.client.get(
            reverse("signup_user")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            "signup.html"
        )

    def test_business_registration_page(self):
        response = self.client.get(
            reverse("signup_business")
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            "Create a business account"
        )

    def test_user_registration(self):
        response = self.client.post(
            reverse("signup_user"),
            self.valid_data
        )

        self.assertRedirects(
            response,
            reverse("signup_success")
        )

        user = MealMateUser.objects.get(
            email="customer@example.com"
        )

        self.assertEqual(
            user.role,
            "user"
        )

        self.assertTrue(
            check_password(
                "SecurePass123!",
                user.password_hash
            )
        )

        self.assertNotEqual(
            user.password_hash,
            "SecurePass123!"
        )

    def test_business_registration(self):
        data = self.valid_data.copy()

        data["full_name"] = "Test Restaurant"
        data["email"] = "business@example.com"

        response = self.client.post(
            reverse("signup_business"),
            data
        )

        self.assertRedirects(
            response,
            reverse("signup_success")
        )

        business = MealMateUser.objects.get(
            email="business@example.com"
        )

        self.assertEqual(
            business.role,
            "business"
        )

    def test_duplicate_email(self):
        self.client.post(
            reverse("signup_user"),
            self.valid_data
        )

        response = self.client.post(
            reverse("signup_business"),
            self.valid_data
        )

        self.assertContains(
            response,
            "An account with this email already exists."
        )

        self.assertEqual(
            MealMateUser.objects.count(),
            1
        )

    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data["confirm_password"] = "WrongPass123!"

        response = self.client.post(
            reverse("signup_user"),
            data
        )

        self.assertContains(
            response,
            "Passwords do not match."
        )

        self.assertEqual(
            MealMateUser.objects.count(),
            0
        )

    def test_short_password(self):
        data = self.valid_data.copy()
        data["password"] = "12345"
        data["confirm_password"] = "12345"

        response = self.client.post(
            reverse("signup_user"),
            data
        )

        self.assertContains(
            response,
            "Password must contain at least 8 characters."
        )

        self.assertEqual(
            MealMateUser.objects.count(),
            0
        )

    def test_registration_does_not_log_in(self):
        self.client.post(
            reverse("signup_user"),
            self.valid_data
        )

        self.assertNotIn(
            "user_id",
            self.client.session
        )
