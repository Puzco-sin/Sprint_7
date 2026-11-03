"""Reusable API test helpers."""

import logging
from datetime import date, timedelta
from uuid import uuid4

import allure
import pytest

logger = logging.getLogger(__name__)


def generate_courier_payload():
    return {
        "login": f"test-courier-{uuid4().hex}",
        "password": f"pass-{uuid4().hex}",
        "firstName": "Тест",
    }


def generate_incorrect_login():
    return f"incorrect-{uuid4().hex}"


def generate_incorrect_password():
    return f"incorrect-{uuid4().hex}"


def generate_missing_login():
    return f"missing-{uuid4().hex}"


def get_order_payloads():
    base_payload = {
        "firstName": "Тест",
        "lastName": "Заказ",
        "address": "Москва, ул. Тестовая, д. 1",
        "metroStation": "4",
        "phone": "+7 800 355 35 35",
        "rentTime": 2,
        "deliveryDate": (date.today() + timedelta(days=2)).isoformat(),
        "comment": "Тестовый заказ",
    }
    return [
        pytest.param({**base_payload, "color": ["BLACK"]}, id="black"),
        pytest.param({**base_payload, "color": ["GREY"]}, id="grey"),
        pytest.param(
            {**base_payload, "color": ["BLACK", "GREY"]},
            id="both-colors",
        ),
        pytest.param(base_payload, id="without-color"),
    ]


@allure.step("Create courier")
def create_courier(api_client, payload, cleanup_couriers):
    cleanup_couriers.append(payload)
    return api_client.create_courier(payload)


@allure.step("Create order")
def create_order(api_client, payload, cleanup_tracks):
    response = api_client.create_order(payload)
    if response.status_code == 201:
        track = response.json().get("track")
        if track is not None:
            cleanup_tracks.add(track)
    return response


@allure.step("Delete test couriers")
def delete_test_couriers(api_client, couriers):
    for courier in couriers:
        login_response = api_client.login_courier(
            {"login": courier["login"], "password": courier["password"]}
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

        delete_response = api_client.delete_courier(courier_id)
        if delete_response.status_code not in (200, 404):
            logger.error(
                "Could not delete test courier %s (HTTP %s): %s",
                courier_id,
                delete_response.status_code,
                delete_response.text,
            )


@allure.step("Cancel test orders")
def cancel_test_orders(api_client, tracks):
    for track in tracks:
        response = api_client.cancel_order(track)
        if response.status_code != 200:
            logger.error(
                "Could not cancel test order %s (HTTP %s): %s",
                track,
                response.status_code,
                response.text,
            )
