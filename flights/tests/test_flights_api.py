from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import Airport, Route, Flight, AirplaneType, Airplane, Crew
from flights.serializers import FlightListSerializer, FlightRetrieveSerializer

FLIGHTS_URL = reverse("flights:flight-list")


def detail_url(flight_id):
    return reverse("flights:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(FLIGHTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)
        self.airport1 = Airport.objects.create(
            name="airport1", closest_big_city="Paris"
        )
        self.airport2 = Airport.objects.create(
            name="airport2", closest_big_city="Berlin"
        )
        self.route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=5000
        )
        self.addition_route = Route.objects.create(
            source=self.airport2, destination=self.airport1, distance=5000
        )
        self.airplane_type = AirplaneType.objects.create(name="type")
        self.airplane = Airplane.objects.create(
            name="test", rows=60, seats_in_row=8, airplane_type=self.airplane_type
        )

    def test_list_flight(self):
        Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=2),
        )

        response = self.client.get(FLIGHTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        flight = response.data["results"][0]
        self.assertEqual(flight["route"], str(self.route))
        self.assertEqual(flight["airplane"], self.airplane.name)

    def test_filter_flights_by_source(self):
        Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=2),
        )
        Flight.objects.create(
            route=self.addition_route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=2),
            arrival_time=timezone.now() + timezone.timedelta(days=3),
        )
        response = self.client.get(FLIGHTS_URL, {"source": "Paris"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        flight = response.data["results"][0]
        self.assertEqual(flight["route"], str(self.route))

    def test_filter_flights_by_destination(self):
        Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=2),
        )
        Flight.objects.create(
            route=self.addition_route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=2),
        )
        response = self.client.get(FLIGHTS_URL, {"destination": "Paris"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        flight = response.data["results"][0]
        self.assertEqual(flight["route"], str(self.addition_route))

    def test_filter_flights_by_departure_time(self):
        Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=2),
        )
        Flight.objects.create(
            route=self.addition_route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=10),
            arrival_time=timezone.now() + timezone.timedelta(days=12),
        )
        response = self.client.get(
            FLIGHTS_URL, {"date": timezone.now().date() + timezone.timedelta(days=1)}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        flight = response.data["results"][0]
        self.assertEqual(flight["route"], str(self.route))

    def test_retrieve_flight(self):
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=2),
        )
        url = detail_url(flight.id)
        response = self.client.get(url)
        serializer = FlightRetrieveSerializer(flight)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now(),
        }
        response = self.client.post(FLIGHTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.airport1 = Airport.objects.create(
            name="airport1", closest_big_city="Paris"
        )
        self.airport2 = Airport.objects.create(
            name="airport2", closest_big_city="Berlin"
        )
        self.route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=5000
        )
        self.airplane_type = AirplaneType.objects.create(name="type")
        self.airplane = Airplane.objects.create(
            name="test", rows=60, seats_in_row=8, airplane_type=self.airplane_type
        )

    def test_create_flight(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now() + timezone.timedelta(days=2),
            "arrival_time": timezone.now() + timezone.timedelta(days=3),
        }
        response = self.client.post(FLIGHTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_flight_with_invalid_departure_time(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() + timezone.timedelta(days=3),
        }
        response = self.client.post(FLIGHTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error_message = (
            "Flights must be created no later " "than a day before departure"
        )
        self.assertIn(expected_error_message, response.data["non_field_errors"])

    def test_create_flight_with_invalid_arrival_time(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now() + timezone.timedelta(days=2),
            "arrival_time": timezone.now(),
        }
        response = self.client.post(FLIGHTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error_message = "Arrival time must be " "later than departure time."
        self.assertIn(expected_error_message, response.data["non_field_errors"])

    def test_update_flight_with_invalid_departure_time(self):
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=2),
        )
        payload = {
            "departure_time": timezone.now() - timezone.timedelta(days=1),
        }
        response = self.client.patch(detail_url(flight.id), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error_message = "Departure time must be in future"
        self.assertIn(expected_error_message, response.data["non_field_errors"])

    def test_create_flight_with_crew(self):
        person1 = Crew.objects.create(first_name="Ann", last_name="Ok")
        person2 = Crew.objects.create(first_name="Bob", last_name="Crab")

        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now() + timezone.timedelta(days=2),
            "arrival_time": timezone.now() + timezone.timedelta(days=3),
            "crew": [person1.id, person2.id],
        }

        response = self.client.post(FLIGHTS_URL, payload)
        flight = Flight.objects.get(id=response.data["id"])

        crew = flight.crew.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(crew.count(), 2)
        self.assertIn(person1, crew)
        self.assertIn(person2, crew)
