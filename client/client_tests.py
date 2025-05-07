import unittest
from client import send_request  # Make sure send_request can be imported like this

class TestSmartHomeClient(unittest.TestCase):
    def test_login(self):
        response = send_request({"action": "login", "username": "user1", "password": "pass1"})
        self.assertEqual(response['status'], 'success')

    def test_logout(self):
        response = send_request({"action": "logout"})
        self.assertEqual(response['status'], 'success')

# Add more tests as necessary

if __name__ == '__main__':
    unittest.main()
