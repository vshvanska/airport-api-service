from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from flights.models import Airport, Route
from flights.serializers import RouteRetrieveSerializer, RouteListSerializer

ROUTE_URL = reverse("flights:route-list")


def detail_url(route_id):
    return reverse("flights:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTest(TestCase):
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

    def test_list_route(self):
        Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=30
        )
        Route.objects.create(
            source=self.airport2, destination=self.airport1, distance=30
        )

        response = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_routes_by_source(self):
        route1 = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=30
        )
        route2 = Route.objects.create(
            source=self.airport2, destination=self.airport1, distance=30
        )

        response = self.client.get(ROUTE_URL, {"source": "Paris"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_filter_routes_by_destination(self):
        route1 = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=30
        )
        route2 = Route.objects.create(
            source=self.airport2, destination=self.airport1, distance=30
        )

        response = self.client.get(ROUTE_URL, {"destination": "Paris"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer1.data, response.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": self.airport2,
            "destination": self.airport1,
            "distance": 30,
        }
        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_route(self):
        route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=30
        )
        url = detail_url(route.id)
        response = self.client.get(url)
        serializer = RouteRetrieveSerializer(route)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AdminRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@user.com", "testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.airport1 = Airport.objects.create(
            name="airport1", closest_big_city="Paris"
        )
        self.airport2 = Airport.objects.create(
            name="airport2", closest_big_city="Berlin"
        )

    def test_list_route(self):
        Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=30
        )
        Route.objects.create(
            source=self.airport2, destination=self.airport1, distance=30
        )

        response = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_route(self):
        payload = {
            "source": self.airport2.id,
            "destination": self.airport1.id,
            "distance": 500,
        }
        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
