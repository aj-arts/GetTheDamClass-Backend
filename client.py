import requests

import requests

BASE_URL = "http://127.0.0.1:5000"

def make_request(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, json=data)
    return response.json()

# Example usage:
if __name__ == "__main__":
    signup_data = {"email": "user@example.com", "pin": "1234"}
    print(make_request("/signup", signup_data))

    subclass_data = {"crn": "12345", "email": "user@example.com", "pin": "1234"}
    print(make_request("/sub", subclass_data))

    unsubclass_data = {"crn": "12345", "email": "user@example.com", "pin": "1234"}
    print(make_request("/unsub", unsubclass_data))