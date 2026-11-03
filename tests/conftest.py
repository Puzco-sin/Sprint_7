import pytest

from api_client import ApiClient
from helpers import cancel_test_orders, delete_test_couriers


@pytest.fixture
def api_client():
    return ApiClient()


@pytest.fixture
def courier_cleanup(api_client):
    couriers = []

    yield couriers

    delete_test_couriers(api_client, couriers)


@pytest.fixture
def order_cleanup(api_client):
    order_tracks = set()

    yield order_tracks

    cancel_test_orders(api_client, order_tracks)
