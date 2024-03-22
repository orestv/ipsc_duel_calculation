import pytest

from litestar.testing import AsyncTestClient

from duels.api import app


@pytest.fixture(scope="session")
async def test_client() -> AsyncTestClient:
    return AsyncTestClient(app=app)