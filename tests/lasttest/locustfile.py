# Aufruf:   uvx locust -f .\tests\lasttest\locustfile.py

#           http://localhost:8089
#           z.B. $env:LOGURU_LEVEL = 'INFO'
#                export LOGURU_LEVEL='INFO'
#           Number of users: 50
#           Ramp Up (users started/second): 5
#           Host: https://localhost:8000

"""Lasttest mit Locust."""

from typing import Final, Literal

import urllib3
from locust import HttpUser, constant_throughput, task

# https://stackoverflow.com/questions/27981545/suppress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho#answer-44615889
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# https://docs.locust.io/en/stable/api.html#httpuser-class
class GetUser(HttpUser):
    """Lasttest für GET-Requests."""

    # https://docs.locust.io/en/stable/writing-a-locustfile.html#wait-time-attribute
    # https://docs.locust.io/en/stable/api.html#locust.User.wait_time
    # https://docs.locust.io/en/stable/api.html#locust.wait_time.constant_throughput
    # 50 "Task Iterations" pro Sekunde
    wait_time = constant_throughput(0.1)
    MIN_USERS: Final = 500
    MAX_USERS: Final = 500

    # https://docs.locust.io/en/stable/writing-a-locustfile.html#on-start-and-on-stop-methods
    def on_start(self) -> None:
        """Start-Skript, um einen JWT im Header für Requests zu speichern."""
        # selbst-signiertes Zertifikat
        self.client.verify = False

        # https://docs.locust.io/en/stable/api.html#httpsession-class
        # https://docs.locust.io/en/stable/api.html#response-class
        # https://requests.readthedocs.io/en/latest/api#requests.Response
        # Login mit der HTTP-Methode QUERY
        response: Final = self.client.request(
            method="QUERY",
            url="/auth/token",
            json={"username": "admin", "password": "p"},
        )
        body: Final[dict[Literal["token"], str]] = response.json()
        token: Final = body["token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})

    # https://docs.locust.io/en/stable/api.html#locust.task
    # https://docs.locust.io/en/stable/api.html#locust.User.weight
    @task(100)
    def get_id(self) -> None:
        """GET-Requests mit einer ID als Pfadparameter."""
        for gast_id in [1, 20, 30, 40, 50, 60]:
            response = self.client.get(f"/rest/{gast_id}")
            print(f"{response.json()['id']}")

    @task(200)
    def get_nachname(self) -> None:
        """GET-Requests mit dem Nachnamen als Query-Parameter."""
        for teil in ["a", "i", "n", "e", "o"]:
            self.client.get("/rest", params={"nachname": teil})

    @task(100)
    def get_nachnamen(self) -> None:
        """GET-Requests mit einem Teilstring als Pfadparameter für Nachnamen."""
        for teil in ["a", "i", "n", "e", "o"]:
            self.client.get(f"/rest/nachnamen/{teil}")

    @task(150)
    def get_email(self) -> None:
        """GET-Requests mit der Emailadresse als Query-Parameter."""
        for email in [
            "admin@acme.com",
            "lena.becker@acme.de",
            "jonas.becker@acme.edu",
            "mia.becker@acme.ch",
            "noah.fischer@acme.uk",
            "emma.wagner@acme.jp",
        ]:
            self.client.get("/rest", params={"email": email})

    @task(50)
    def get_all(self) -> None:
        """GET-Request für eine Seite aller Gäste (nur ADMIN)."""
        self.client.get("/rest", params={"size": 5})
