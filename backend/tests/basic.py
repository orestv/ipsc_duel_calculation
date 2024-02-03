from litestar.status_codes import HTTP_405_METHOD_NOT_ALLOWED
from litestar.testing import TestClient


def test_calculate_duels(test_client: TestClient) -> None:
    with test_client as client:
        response = client.get("/duels")
        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED