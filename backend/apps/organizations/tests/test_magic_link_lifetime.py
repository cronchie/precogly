"""Tests that MagicLinkViewSet sets a new share link's expiry from
MAGIC_LINK_LIFETIME_DAYS."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.organizations.models import MagicLink, Organization, OrganizationMember
from apps.threat_models.models import ThreatModel

User = get_user_model()


class MagicLinkLifetimeTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org = Organization.objects.create(name="Acme")
        cls.owner = User.objects.create_user(
            username="owner", email="owner@acme.test", password="pw"
        )
        OrganizationMember.objects.create(
            organization=cls.org, user=cls.owner, role="security_team"
        )
        cls.threat_model = ThreatModel.objects.create(
            organization=cls.org, created_by=cls.owner, name="Published model"
        )

    def setUp(self):
        self.client.force_authenticate(self.owner)

    @override_settings(MAGIC_LINK_LIFETIME_DAYS=365)
    def test_link_expiry_uses_configured_lifetime(self):
        before = timezone.now()
        response = self.client.post(
            "/api/magic-links/", {"threatModel": self.threat_model.id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        link = MagicLink.objects.get(threat_model=self.threat_model)
        self.assertGreaterEqual(link.expires_at, before + timedelta(days=365))
        self.assertLess(link.expires_at, before + timedelta(days=366))
