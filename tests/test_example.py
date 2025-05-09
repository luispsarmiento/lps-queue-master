import unittest
from app import create_app

class ExampleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_example_route(self):
        response = self.client.get('/example')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello from the controller!', response.data)