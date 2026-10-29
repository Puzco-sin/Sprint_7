import os
import random
import string
from datetime import date, timedelta
from uuid import uuid4

import pytest
import requests


API_BASE_URL = os.getenv(
    "SCOOTER_API_BASE_URL",
    "https://qa-scooter.education-services.ru/api/v1",
).rstrip("/")


def register_new_courier_and_return_login_password():
    def generate_random_string(length):
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(length))
        return random_string

    login_pass = []

    login = generate_random_string(10)
    password = generate_random_string(10)
    first_name = generate_random_string(10)

    payload = {
        "login": login,
        "password": password,
        "firstName": first_name
    }

    response = requests.post(f"{API_BASE_URL}/courier", data=payload)

    if response.status_code == 201:
        login_pass.append(login)
        login_pass.append(password)
        login_pass.append(first_name)

    return login_pass


@pytest.fixture
def api_request():
    def request(method, path, **kwargs):
        return requests.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=15,
            **kwargs,
        )

    return request


@pytest.fixture
def courier_payload():
    return {
        "login": f"test-courier-{uuid4().hex}",
        "password": f"pass-{uuid4().hex}",
        "firstName": "Тест",
    }


@pytest.fixture
def courier_ids(api_request):
    courier_ids = set()

    yield courier_ids

    for courier_id in courier_ids:
        response = api_request("DELETE", f"/courier/{courier_id}")
        assert response.status_code in (200, 404), response.text


@pytest.fixture
def courier_factory(api_request, courier_ids):
    def create(payload):
        response = api_request("POST", "/courier", json=payload)
        if response.status_code == 201:
            login_response = api_request(
                "POST",
                "/courier/login",
                json={"login": payload["login"], "password": payload["password"]},
            )
            assert login_response.status_code == 200, login_response.text
            courier_ids.add(login_response.json()["id"])
        return response

    yield create


@pytest.fixture
def registered_courier(api_request, courier_ids):
    credentials = register_new_courier_and_return_login_password()
    assert credentials, "Не удалось зарегистрировать уникального курьера"
    login, password, first_name = credentials

    login_response = api_request(
        "POST",
        "/courier/login",
        json={"login": login, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    courier_ids.add(login_response.json()["id"])

    return {
        "login": login,
        "password": password,
        "firstName": first_name,
        "id": login_response.json()["id"],
    }


@pytest.fixture
def order_payload():
    return {
        "firstName": "Тест",
        "lastName": "Заказ",
        "address": "Москва, ул. Тестовая, д. 1",
        "metroStation": "4",
        "phone": "+7 800 355 35 35",
        "rentTime": 2,
        "deliveryDate": (date.today() + timedelta(days=2)).isoformat(),
        "comment": "Тестовый заказ",
    }


@pytest.fixture
def order_factory(api_request):
    tracks = set()

    def create(payload):
        response = api_request("POST", "/orders", json=payload)
        if response.status_code == 201:
            track = response.json().get("track")
            if track is not None:
                tracks.add(track)
        return response

    yield create

    for track in tracks:
        response = api_request("PUT", "/orders/cancel", params={"track": track})
        assert response.status_code == 200, response.text
