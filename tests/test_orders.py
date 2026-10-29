import pytest


class TestCreateOrder:
    @pytest.mark.parametrize(
        "color",
        [
            pytest.param(["BLACK"], id="black"),
            pytest.param(["GREY"], id="grey"),
            pytest.param(["BLACK", "GREY"], id="both-colors"),
            pytest.param(None, id="without-color"),
        ],
    )
    def test_order_creation_returns_success_status(
        self, color, order_factory, order_payload
    ):
        payload = {**order_payload}
        if color is not None:
            payload["color"] = color

        response = order_factory(payload)

        assert response.status_code == 201

    @pytest.mark.parametrize(
        "color",
        [
            pytest.param(["BLACK"], id="black"),
            pytest.param(["GREY"], id="grey"),
            pytest.param(["BLACK", "GREY"], id="both-colors"),
            pytest.param(None, id="without-color"),
        ],
    )
    def test_order_creation_response_contains_track(
        self, color, order_factory, order_payload
    ):
        payload = {**order_payload}
        if color is not None:
            payload["color"] = color

        response = order_factory(payload)

        assert "track" in response.json()


class TestGetOrders:
    def test_orders_list_returns_success_status(self, api_request):
        response = api_request("GET", "/orders", params={"limit": 1})

        assert response.status_code == 200

    def test_orders_list_response_contains_a_list(self, api_request):
        response = api_request("GET", "/orders", params={"limit": 1})

        assert isinstance(response.json()["orders"], list)
