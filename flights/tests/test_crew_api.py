from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import Crew
from flights.serializers import CrewSerializer

CREW_URL = reverse("flights:crew-list")


def sample_crew(**params):
    defaults = {"first_name": "Alex", "last_name": "Black"}
    defaults.update(params)

    return Crew.objects.create(**defaults)


def detail_url(crew_id):
    return reverse("flights:crew-detail", args=[crew_id])


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_admin_required(self):
        sample_crew()
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@user.com", "testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew(first_name="crew1")
        sample_crew(last_name="crew2")

        response = self.client.get(CREW_URL)
        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_crew(self):
        payload = {
            "first_name": "test",
            "last_name": "crew",
        }
        response = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_update_crew(self):
        crew = sample_crew()
        url = detail_url(crew.id)
        payload = {"first_name": "Name", "last_name": "Last name"}
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        crew = Crew.objects.get(id=response.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_delete_crew(self):
        crew = sample_crew()
        url = detail_url(crew.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
