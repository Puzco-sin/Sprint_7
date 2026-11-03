"""HTTP client for the scooter API."""

import allure
import requests

from constants import (
    API_BASE_URL,
    CANCEL_ORDER_ENDPOINT,
    CREATE_COURIER_ENDPOINT,
    DELETE_COURIER_ENDPOINT,
    LOGIN_COURIER_ENDPOINT,
    ORDERS_ENDPOINT,
)


class ApiClient:
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    @allure.step("Send {method} request to {endpoint}")
    def _request(self, method, endpoint, **kwargs):
        return requests.request(
            method,
            f"{self.base_url}{endpoint}",
            timeout=30,
            **kwargs,
        )

    @allure.step("Create courier")
    def create_courier(self, payload):
        return self._request("POST", CREATE_COURIER_ENDPOINT, json=payload)

    @allure.step("Log in courier")
    def login_courier(self, credentials):
        return self._request("POST", LOGIN_COURIER_ENDPOINT, json=credentials)

    @allure.step("Delete courier {courier_id}")
    def delete_courier(self, courier_id):
        return self._request(
            "DELETE", DELETE_COURIER_ENDPOINT.format(courier_id)
        )

    @allure.step("Create order")
    def create_order(self, payload):
        return self._request("POST", ORDERS_ENDPOINT, json=payload)

    @allure.step("Cancel order with track {track}")
    def cancel_order(self, track):
        return self._request(
            "PUT", CANCEL_ORDER_ENDPOINT, params={"track": track}
        )

    @allure.step("Get orders")
    def get_orders(self, **params):
        return self._request("GET", ORDERS_ENDPOINT, params=params)
