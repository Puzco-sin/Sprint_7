import allure
import pytest

from helpers import create_order, get_order_payloads


class TestCreateOrder:
    @allure.title("Создание заказа для каждого варианта цвета")
    @pytest.mark.parametrize(
        "payload",
        get_order_payloads(),
    )
    def test_order_creation_returns_success_status(
        self, api_client, payload, order_cleanup
    ):
        response = create_order(api_client, payload, order_cleanup)

        assert response.status_code == 201

    @allure.title("Ответ создания заказа содержит track для каждого цвета")
    @pytest.mark.parametrize(
        "payload",
        get_order_payloads(),
    )
    def test_order_creation_response_contains_track(
        self, api_client, payload, order_cleanup
    ):
        response = create_order(api_client, payload, order_cleanup)

        assert "track" in response.json()


class TestGetOrders:
    @allure.title("Получение списка заказов: успешный статус ответа")
    def test_orders_list_returns_success_status(self, api_client):
        response = api_client.get_orders(limit=1)

        assert response.status_code == 200

    @allure.title("Получение списка заказов: ответ содержит список")
    def test_orders_list_response_contains_a_list(self, api_client):
        response = api_client.get_orders(limit=1)

        assert isinstance(response.json()["orders"], list)
