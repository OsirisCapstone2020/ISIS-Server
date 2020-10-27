import requests

from .conftest import DEV_SERVER_ADDR


class TestServer:
    def test_get_index(self):
        resp = requests.get(DEV_SERVER_ADDR)

        # Request OK
        resp.raise_for_status()

        # Correct Content-Type
        assert resp.headers["Content-Type"].startswith("application/json")

