from datetime import date, timedelta

import allure
import pytest

from constants import ORDERS_ENDPOINT


BASE_ORDER_PAYLOAD = {
    "firstName": "Тест",
    "lastName": "Заказ",
    "address": "Москва, ул. Тестовая, д. 1",
    "metroStation": "4",
    "phone": "+7 800 355 35 35",
    "rentTime": 2,
    "deliveryDate": (date.today() + timedelta(days=2)).isoformat(),
    "comment": "Тестовый заказ",
}
ORDER_PAYLOADS = [
    pytest.param(
        {**BASE_ORDER_PAYLOAD, "color": ["BLACK"]},
        id="black",
    ),
    pytest.param(
        {**BASE_ORDER_PAYLOAD, "color": ["GREY"]},
        id="grey",
    ),
    pytest.param(
        {**BASE_ORDER_PAYLOAD, "color": ["BLACK", "GREY"]},
        id="both-colors",
    ),
    pytest.param(BASE_ORDER_PAYLOAD, id="without-color"),
]


class TestCreateOrder:
    @allure.title("Создание заказа для каждого варианта цвета")
    @pytest.mark.parametrize(
        "payload",
        ORDER_PAYLOADS,
    )
    def test_order_creation_returns_success_status(self, payload, order_factory):
        response = order_factory(payload)

        assert response.status_code == 201

    @allure.title("Ответ создания заказа содержит track для каждого цвета")
    @pytest.mark.parametrize(
        "payload",
        ORDER_PAYLOADS,
    )
    def test_order_creation_response_contains_track(self, payload, order_factory):
        response = order_factory(payload)

        assert "track" in response.json()


class TestGetOrders:
    @allure.title("Получение списка заказов: успешный статус ответа")
    def test_orders_list_returns_success_status(self, api_request):
        response = api_request("GET", ORDERS_ENDPOINT, params={"limit": 1})

        assert response.status_code == 200

    @allure.title("Получение списка заказов: ответ содержит список")
    def test_orders_list_response_contains_a_list(self, api_request):
        response = api_request("GET", ORDERS_ENDPOINT, params={"limit": 1})

        assert isinstance(response.json()["orders"], list)
