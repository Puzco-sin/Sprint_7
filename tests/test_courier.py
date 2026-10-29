import copy
from uuid import uuid4

import pytest


class TestCreateCourier:
    def test_create_courier_returns_success_status(
        self, courier_factory, courier_payload
    ):
        response = courier_factory(courier_payload)

        assert response.status_code == 201

    def test_create_courier_returns_success_body(
        self, courier_factory, courier_payload
    ):
        response = courier_factory(courier_payload)

        assert response.json() == {"ok": True}

    def test_cannot_create_couriers_with_same_login(
        self, registered_courier, api_request
    ):
        response = api_request(
            "POST",
            "/courier",
            json={
                "login": registered_courier["login"],
                "password": registered_courier["password"],
                "firstName": registered_courier["firstName"],
            },
        )

        assert response.status_code == 409

    def test_courier_can_be_created_without_first_name(
        self, courier_factory, courier_payload
    ):
        payload = copy.deepcopy(courier_payload)
        payload.pop("firstName")

        response = courier_factory(payload)

        assert response.status_code == 201

    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_cannot_create_courier_without_required_field(
        self, api_request, courier_payload, missing_field
    ):
        payload = copy.deepcopy(courier_payload)
        payload.pop(missing_field)

        response = api_request("POST", "/courier", json=payload)

        assert response.status_code == 400


class TestLoginCourier:
    def test_courier_login_returns_success_status(
        self, registered_courier, api_request
    ):
        response = api_request(
            "POST",
            "/courier/login",
            json={
                "login": registered_courier["login"],
                "password": registered_courier["password"],
            },
        )

        assert response.status_code == 200

    def test_courier_login_returns_id(self, registered_courier, api_request):
        response = api_request(
            "POST",
            "/courier/login",
            json={
                "login": registered_courier["login"],
                "password": registered_courier["password"],
            },
        )

        assert response.json()["id"] == registered_courier["id"]

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            pytest.param("login", "incorrect-login", id="wrong-login"),
            pytest.param("password", "incorrect-password", id="wrong-password"),
        ],
    )
    def test_courier_cannot_log_in_with_incorrect_credentials(
        self, registered_courier, api_request, field, value
    ):
        credentials = {
            "login": registered_courier["login"],
            "password": registered_courier["password"],
        }
        credentials[field] = f"{value}-{uuid4().hex}" if field == "login" else value

        response = api_request("POST", "/courier/login", json=credentials)

        assert response.status_code == 404

    def test_nonexistent_courier_cannot_log_in(self, api_request):
        response = api_request(
            "POST",
            "/courier/login",
            json={
                "login": f"missing-{uuid4().hex}",
                "password": "unknown-password",
            },
        )

        assert response.status_code == 404

    @pytest.mark.parametrize("missing_field", ["login", "password"])
    def test_courier_cannot_log_in_without_required_field(
        self, registered_courier, api_request, missing_field
    ):
        credentials = {
            "login": registered_courier["login"],
            "password": registered_courier["password"],
        }
        credentials.pop(missing_field)

        response = api_request("POST", "/courier/login", json=credentials)

        assert response.status_code == 400
