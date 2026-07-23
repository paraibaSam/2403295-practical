import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import app, is_attack

class ValidationTests(unittest.TestCase):
    def test_valid_input_passes(self):
        self.assertFalse(is_attack("hello world"))

    def test_sql_injection_blocked(self):
        self.assertTrue(is_attack("' OR 1=1 --"))

    def test_xss_blocked(self):
        self.assertTrue(is_attack("<script>alert(1)</script>"))

    def test_too_long_blocked(self):
        self.assertTrue(is_attack("a" * 101))

    def test_empty_blocked(self):
        self.assertTrue(is_attack(""))


class RouteIntegrationTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.auth = {"Authorization": "Basic YWRtaW46MjQwMzI5NUBTSVQuc2luZ2Fwb3JldGVjaC5lZHUuc2c="}

    def test_home_requires_auth(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 401)

    def test_home_loads_with_auth(self):
        response = self.client.get("/", headers=self.auth)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()