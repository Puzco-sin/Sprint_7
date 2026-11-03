import allure
import pytest

from helpers import (
    create_courier,
    generate_incorrect_login,
    generate_incorrect_password,
    generate_missing_login,
    generate_courier_payload,
)


class TestCreateCourier:
    @allure.title("Создание курьера: успешный статус ответа")
    def test_create_courier_returns_success_status(
        self, api_client, courier_cleanup
    ):
        response = create_courier(
            api_client, generate_courier_payload(), courier_cleanup
        )

        assert response.status_code == 201

    @allure.title("Создание курьера: успешное тело ответа")
    def test_create_courier_returns_success_body(
        self, api_client, courier_cleanup
    ):
        response = create_courier(
            api_client, generate_courier_payload(), courier_cleanup
        )

        assert response.json() == {"ok": True}

    @allure.title("Создание курьера с уже занятым логином")
    def test_cannot_create_couriers_with_same_login(
        self, api_client, courier_cleanup
    ):
        payload = generate_courier_payload()
        create_courier(api_client, payload, courier_cleanup).raise_for_status()
        response = api_client.create_courier(payload)

        assert response.status_code == 409

    @allure.title("Создание курьера без имени")
    def test_courier_can_be_created_without_first_name(
        self, api_client, courier_cleanup
    ):
        payload = generate_courier_payload()
        payload.pop("firstName")

        response = create_courier(api_client, payload, courier_cleanup)

        assert response.status_code == 201

    @allure.title("Создание курьера без обязательного поля: {missing_field}")
    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_cannot_create_courier_without_required_field(
        self, api_client, missing_field
    ):
        payload = generate_courier_payload()
        payload.pop(missing_field)

        response = api_client.create_courier(payload)

        assert response.status_code == 400


class TestLoginCourier:
    @allure.title("Логин курьера: успешный статус ответа")
    def test_courier_login_returns_success_status(
        self, api_client, courier_cleanup
    ):
        payload = generate_courier_payload()
        create_courier(api_client, payload, courier_cleanup).raise_for_status()

        response = api_client.login_courier(
            {
                "login": payload["login"],
                "password": payload["password"],
            }
        )

        assert response.status_code == 200

    @allure.title("Логин курьера: ответ содержит id")
    def test_courier_login_returns_id(
        self, api_client, courier_cleanup
    ):
        payload = generate_courier_payload()
        create_courier(api_client, payload, courier_cleanup).raise_for_status()

        response = api_client.login_courier(
            {
                "login": payload["login"],
                "password": payload["password"],
            }
        )

        assert "id" in response.json()

    @allure.title("Логин курьера с неверным логином")
    def test_courier_cannot_log_in_with_incorrect_login(
        self, api_client, courier_cleanup
    ):
        payload = generate_courier_payload()
        create_courier(api_client, payload, courier_cleanup).raise_for_status()

        response = api_client.login_courier(
            {
                "login": generate_incorrect_login(),
                "password": payload["password"],
            }
        )

        assert response.status_code == 404

    @allure.title("Логин курьера с неверным паролем")
    def test_courier_cannot_log_in_with_incorrect_password(
        self, api_client, courier_cleanup
    ):
        payload = generate_courier_payload()
        create_courier(api_client, payload, courier_cleanup).raise_for_status()

        response = api_client.login_courier(
            {
                "login": payload["login"],
                "password": generate_incorrect_password(),
            }
        )

        assert response.status_code == 404

    @allure.title("Логин несуществующего курьера")
    def test_nonexistent_courier_cannot_log_in(self, api_client):
        response = api_client.login_courier(
            {
                "login": generate_missing_login(),
                "password": "unknown-password",
            }
        )

        assert response.status_code == 404

    @allure.title("Логин курьера без обязательного поля: {missing_field}")
    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_courier_cannot_log_in_without_required_field(
        self, api_client, missing_field, courier_cleanup
    ):
        payload = generate_courier_payload()
        create_courier(api_client, payload, courier_cleanup).raise_for_status()

        credentials = {
            "login": payload["login"],
            "password": payload["password"],
        }
        credentials.pop(missing_field)

        response = api_client.login_courier(credentials)

        assert response.status_code == 400
