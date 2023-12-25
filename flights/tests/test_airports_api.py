from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import Airport
from flights.serializers import AirportSerializer

AIRPORT_URL = reverse("flights:airport-list")


def sample_airport(**params):
    defaults = {"name": "test_airport", "closest_big_city": "City"}
    defaults.update(params)

    return Airport.objects.create(**defaults)


def detail_url(airport_id):
    return reverse("flights:airport-detail", args=[airport_id])


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list_airport(self):
        sample_airport(name="airport1")
        sample_airport(name="airport2")

        response = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_airports_by_closest_big_city(self):
        airport1 = sample_airport(name="airport1", closest_big_city="Rome")
        airport2 = sample_airport(name="airport2", closest_big_city="London")

        response = self.client.get(AIRPORT_URL, {"city": "rome"})

        serializer1 = AirportSerializer(airport1)
        serializer2 = AirportSerializer(airport2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "test airport create",
            "closest_big_city": "Paris",
        }
        response = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@user.com", "testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airport(self):
        payload = {
            "name": "test airport create",
            "closest_big_city": "Paris",
        }
        response = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(airport, key))
