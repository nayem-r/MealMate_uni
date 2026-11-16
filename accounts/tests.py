
from django.contrib.auth.hashers import check_password, make_password
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
        response = self.client.get(reverse("signup_user"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")

    def test_business_registration_page(self):
        response = self.client.get(reverse("signup_business"))

        self.assertEqual(response.status_code, 200)
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

        self.assertEqual(user.role, "user")
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

        self.assertEqual(business.role, "business")

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


class LoginTests(TestCase):
    def setUp(self):
        self.user = MealMateUser.objects.create(
            full_name="Test Customer",
            email="customer@example.com",
            password_hash=make_password("SecurePass123!"),
            role="user",
            is_active=True,
        )

    def login(self):
        return self.client.post(
            reverse("login"),
            {
                "email": "customer@example.com",
                "password": "SecurePass123!",
            }
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_user_can_log_in(self):
        response = self.login()

        self.assertRedirects(
            response,
            reverse("dashboard")
        )

        self.assertEqual(
            self.client.session["user_id"],
            self.user.id
        )

        self.assertEqual(
            self.client.session["user_role"],
            "user"
        )

    def test_business_can_log_in(self):
        self.user.role = "business"
        self.user.save(update_fields=["role"])

        response = self.login()

        self.assertRedirects(
            response,
            reverse("home")
        )

        self.assertEqual(
            self.client.session["user_role"],
            "business"
        )

    def test_incorrect_password_is_rejected(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "customer@example.com",
                "password": "IncorrectPassword!",
            }
        )

        self.assertContains(
            response,
            "Incorrect email or password."
        )

        self.assertNotIn(
            "user_id",
            self.client.session
        )

    def test_inactive_account_is_rejected(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.login()

        self.assertContains(
            response,
            "This account is inactive."
        )

        self.assertNotIn(
            "user_id",
            self.client.session
        )

    def test_homepage_displays_logged_in_user(self):
        self.login()

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Test Customer")
        self.assertContains(response, "Log Out")

    def test_logout_clears_session(self):
        self.login()

        response = self.client.post(reverse("logout"))

        self.assertRedirects(
            response,
            reverse("home")
        )

        self.assertNotIn(
            "user_id",
            self.client.session
        )

    def test_logout_requires_post(self):
        self.login()

        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            self.client.session["user_id"],
            self.user.id
        )


class FoodSeekerDashboardTests(TestCase):
    def setUp(self):
        self.user = MealMateUser.objects.create(
            full_name="Food Seeker",
            email="seeker@example.com",
            password_hash=make_password("SecurePass123!"),
            role="user",
            is_active=True,
        )

        self.business = MealMateUser.objects.create(
            full_name="Test Restaurant",
            email="business@example.com",
            password_hash=make_password("SecurePass123!"),
            role="business",
            is_active=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(
            reverse("dashboard")
        )

        self.assertRedirects(
            response,
            reverse("login")
        )

    def test_food_seeker_can_access_dashboard(self):
        self.client.post(
            reverse("login"),
            {
                "email": "seeker@example.com",
                "password": "SecurePass123!",
            }
        )

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertContains(response, "Welcome, Food Seeker")
        self.assertContains(response, "Food Marketplace")

    def test_business_cannot_access_food_seeker_dashboard(self):
        self.client.post(
            reverse("login"),
            {
                "email": "business@example.com",
                "password": "SecurePass123!",
            }
        )

        response = self.client.get(
            reverse("dashboard")
        )

        self.assertRedirects(
            response,
            reverse("home")
        )

    def test_logged_in_food_seeker_is_redirected_to_dashboard(self):
        self.client.post(
            reverse("login"),
            {
                "email": "seeker@example.com",
                "password": "SecurePass123!",
            }
        )

        response = self.client.get(
            reverse("login")
        )

        self.assertRedirects(
            response,
            reverse("dashboard")
        )
