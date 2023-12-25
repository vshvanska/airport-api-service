from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import Airplane, AirplaneType
from flights.serializers import AirplaneListSerializer

AIRPLANE_URL = reverse("flights:airplane-list")


def sample_airplane_type(**params):
    defaults = {"name": "test_type"}
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane(self):
        airplane_type = sample_airplane_type()
        Airplane.objects.create(
            name="test", rows=60, seats_in_row=8, airplane_type=airplane_type
        )

        response = self.client.get(AIRPLANE_URL)
        routes = Airplane.objects.all()
        serializer = AirplaneListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_admin_required(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "test",
            "rows": 40,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@user.com", "testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.airplane_type = sample_airplane_type(name="type1")

    def test_create_airplane(self):
        payload = {
            "name": "test",
            "rows": 40,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
