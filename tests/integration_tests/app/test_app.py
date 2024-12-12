import unittest

from immo_rechner.app.app import get_app


class TestAppHealthCheck(unittest.TestCase):

    def setUp(self):
        # Create a test client for the Flask server
        self.server = get_app().server.test_client()

    def test_health_check(self):
        # When: Checking health endpoint
        response = self.server.get("/health")

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the response JSON contains the expected data
        self.assertEqual(response.json, {"status": "healthy"})

    def test_homepage_load(self):
        # When: Send a GET request to the homepage
        response = self.server.get("/")

        # Check if the status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the response contains Dash's default content (e.g., HTML structure)
        self.assertIn(b"dash-renderer", response.data)
