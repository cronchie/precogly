"""Tests for the REGISTRATION_ENABLED switch on the signup API.

An operator who publishes threat models through share links turns registration
off. Anyone can call the signup API without the signup page, so these tests check
that the API itself refuses to create accounts.
"""

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

REGISTER_URL = "/api/auth/registration/"


class RegistrationEnabledTests(APITestCase):
    def _register(self):
        return self.client.post(
            REGISTER_URL,
            {
                # The frontend's signup form sends the email as the username too
                "username": "new@example.test",
                "email": "new@example.test",
                "password1": "a-Strong-passw0rd!",
                "password2": "a-Strong-passw0rd!",
            },
            format="json",
        )

    @override_settings(REGISTRATION_ENABLED=True)
    def test_registration_creates_account_when_enabled(self):
        response = self._register()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.test").exists())

    @override_settings(REGISTRATION_ENABLED=False)
    def test_registration_refused_when_disabled(self):
        response = self._register()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"], "Registration is disabled on this instance."
        )
        self.assertFalse(User.objects.filter(email="new@example.test").exists())
