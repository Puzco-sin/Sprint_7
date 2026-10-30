import logging
from uuid import uuid4

import allure
import pytest
import requests

from constants import (
    API_BASE_URL,
    CANCEL_ORDER_ENDPOINT,
    DELETE_COURIER_ENDPOINT,
    LOGIN_COURIER_ENDPOINT,
    ORDERS_ENDPOINT,
)

logger = logging.getLogger(__name__)


@pytest.fixture
def api_request():
    @allure.step("API request: {method} {path}")
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
def courier_cleanup(api_request):
    couriers = []

    yield couriers

    for courier in couriers:
        login_response = api_request(
            "POST",
            LOGIN_COURIER_ENDPOINT,
            json={"login": courier["login"], "password": courier["password"]},
        )
        if login_response.status_code != 200:
            logger.error(
                "Could not log in to delete test courier (HTTP %s): %s",
                login_response.status_code,
                login_response.text,
            )
            continue

        courier_id = login_response.json().get("id")
        if courier_id is None:
            logger.error("Login response for test courier does not contain id")
            continue

        delete_response = api_request(
            "DELETE", DELETE_COURIER_ENDPOINT.format(courier_id)
        )
        if delete_response.status_code not in (200, 404):
            logger.error(
                "Could not delete test courier %s (HTTP %s): %s",
                courier_id,
                delete_response.status_code,
                delete_response.text,
            )


@pytest.fixture
def order_factory(api_request):
    tracks = set()

    def create(payload):
        response = api_request("POST", ORDERS_ENDPOINT, json=payload)
        if response.status_code == 201:
            track = response.json().get("track")
            if track is not None:
                tracks.add(track)
        return response

    yield create

    for track in tracks:
        response = api_request(
            "PUT", CANCEL_ORDER_ENDPOINT, params={"track": track}
        )
        if response.status_code != 200:
            logger.error(
                "Could not cancel test order %s (HTTP %s): %s",
                track,
                response.status_code,
                response.text,
            )
