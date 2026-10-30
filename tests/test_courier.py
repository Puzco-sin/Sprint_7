import copy
from uuid import uuid4

import allure
import pytest

from constants import CREATE_COURIER_ENDPOINT, LOGIN_COURIER_ENDPOINT


@allure.step("Создать курьера для предусловия теста")
def create_courier_for_test(api_request, courier_payload, courier_cleanup):
    courier_cleanup.append(courier_payload)
    response = api_request(
        "POST", CREATE_COURIER_ENDPOINT, json=courier_payload
    )
    response.raise_for_status()


class TestCreateCourier:
    @allure.title("Создание курьера: успешный статус ответа")
    def test_create_courier_returns_success_status(
        self, api_request, courier_payload, courier_cleanup
    ):
        courier_cleanup.append(courier_payload)
        response = api_request(
            "POST", CREATE_COURIER_ENDPOINT, json=courier_payload
        )

        assert response.status_code == 201

    @allure.title("Создание курьера: успешное тело ответа")
    def test_create_courier_returns_success_body(
        self, api_request, courier_payload, courier_cleanup
    ):
        courier_cleanup.append(courier_payload)
        response = api_request(
            "POST", CREATE_COURIER_ENDPOINT, json=courier_payload
        )

        assert response.json() == {"ok": True}

    @allure.title("Создание курьера с уже занятым логином")
    def test_cannot_create_couriers_with_same_login(
        self, api_request, courier_payload, courier_cleanup
    ):
        create_courier_for_test(api_request, courier_payload, courier_cleanup)
        response = api_request(
            "POST", CREATE_COURIER_ENDPOINT, json=courier_payload
        )

        assert response.status_code == 409

    @allure.title("Создание курьера без имени")
    def test_courier_can_be_created_without_first_name(
        self, api_request, courier_payload, courier_cleanup
    ):
        payload = copy.deepcopy(courier_payload)
        payload.pop("firstName")
        courier_cleanup.append(payload)

        response = api_request("POST", CREATE_COURIER_ENDPOINT, json=payload)

        assert response.status_code == 201

    @allure.title("Создание курьера без обязательного поля: {missing_field}")
    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_cannot_create_courier_without_required_field(
        self, api_request, courier_payload, missing_field
    ):
        payload = copy.deepcopy(courier_payload)
        payload.pop(missing_field)

        response = api_request("POST", CREATE_COURIER_ENDPOINT, json=payload)

        assert response.status_code == 400


class TestLoginCourier:
    @allure.title("Логин курьера: успешный статус ответа")
    def test_courier_login_returns_success_status(
        self, api_request, courier_payload, courier_cleanup
    ):
        create_courier_for_test(api_request, courier_payload, courier_cleanup)

        response = api_request(
            "POST",
            LOGIN_COURIER_ENDPOINT,
            json={
                "login": courier_payload["login"],
                "password": courier_payload["password"],
            },
        )

        assert response.status_code == 200

    @allure.title("Логин курьера: ответ содержит id")
    def test_courier_login_returns_id(
        self, api_request, courier_payload, courier_cleanup
    ):
        create_courier_for_test(api_request, courier_payload, courier_cleanup)

        response = api_request(
            "POST",
            LOGIN_COURIER_ENDPOINT,
            json={
                "login": courier_payload["login"],
                "password": courier_payload["password"],
            },
        )

        assert "id" in response.json()

    @allure.title("Логин курьера с неверным логином")
    def test_courier_cannot_log_in_with_incorrect_login(
        self, api_request, courier_payload, courier_cleanup
    ):
        create_courier_for_test(api_request, courier_payload, courier_cleanup)

        response = api_request(
            "POST",
            LOGIN_COURIER_ENDPOINT,
            json={
                "login": f"incorrect-{uuid4().hex}",
                "password": courier_payload["password"],
            },
        )

        assert response.status_code == 404

    @allure.title("Логин курьера с неверным паролем")
    def test_courier_cannot_log_in_with_incorrect_password(
        self, api_request, courier_payload, courier_cleanup
    ):
        create_courier_for_test(api_request, courier_payload, courier_cleanup)

        response = api_request(
            "POST",
            LOGIN_COURIER_ENDPOINT,
            json={
                "login": courier_payload["login"],
                "password": f"incorrect-{uuid4().hex}",
            },
        )

        assert response.status_code == 404

    @allure.title("Логин несуществующего курьера")
    def test_nonexistent_courier_cannot_log_in(self, api_request):
        response = api_request(
            "POST",
            LOGIN_COURIER_ENDPOINT,
            json={
                "login": f"missing-{uuid4().hex}",
                "password": "unknown-password",
            },
        )

        assert response.status_code == 404

    @allure.title("Логин курьера без обязательного поля: {missing_field}")
    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_courier_cannot_log_in_without_required_field(
        self, api_request, courier_payload, courier_cleanup, missing_field
    ):
        create_courier_for_test(api_request, courier_payload, courier_cleanup)

        credentials = {
            "login": courier_payload["login"],
            "password": courier_payload["password"],
        }
        credentials.pop(missing_field)

        response = api_request(
            "POST", LOGIN_COURIER_ENDPOINT, json=credentials
        )

        assert response.status_code == 400
