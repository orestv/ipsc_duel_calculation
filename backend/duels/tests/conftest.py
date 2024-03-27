import dataclasses
import uuid

import litestar.status_codes
import pytest

from litestar.testing import AsyncTestClient

import duels.model
from duels.api import app
from duels.api_models import MatchSetup, MatchInProgress, RangeSetup, ClassSetup, Duels, MatchCreate
from duels.model import Class


@pytest.fixture(scope="session")
async def test_client() -> AsyncTestClient:
    return AsyncTestClient(app=app)


@dataclasses.dataclass
class MatchSetupFixture:
    match_setup: MatchSetup
    participants: dict[duels.model.Class, list[str]]


@dataclasses.dataclass
class MatchOutcomeFixture:
    match_setup_fixture: MatchSetupFixture
    match_id: uuid.UUID
    match_in_progress: MatchInProgress


@pytest.fixture(scope="function")
def match_setup_fixture(faker) -> MatchSetupFixture:
    participant_names = list({faker.first_name() for _ in range(10)})
    match_setup = MatchSetup(
        ranges={
            "1": RangeSetup(
                classes={
                    Class.STANDARD: ClassSetup(
                        participants=participant_names,
                        times=2,
                    )
                }
            )
        }
    )
    return MatchSetupFixture(
        participants={Class.STANDARD: participant_names},
        match_setup=match_setup,
    )


@pytest.fixture(scope="function")
async def match_outcome_fixture(test_client: AsyncTestClient, faker, match_setup_fixture) -> MatchOutcomeFixture:
    duels_response = await test_client.post("/api/duels", content=match_setup_fixture.match_setup.json())
    assert duels_response.status_code == litestar.status_codes.HTTP_201_CREATED
    duels = Duels.parse_obj(duels_response.json())

    match = MatchCreate(
        name=faker.bs(),
        duels=duels,
    )
    create_response = await test_client.post("/api/matches", content=match.json())
    assert create_response.status_code == litestar.status_codes.HTTP_201_CREATED
    match_id = uuid.UUID(create_response.json())

    match_response = await test_client.get(f"/api/matches/{match_id}")
    assert match_response.status_code == litestar.status_codes.HTTP_200_OK
    match_in_progress = MatchInProgress.parse_obj(match_response.json())
    return MatchOutcomeFixture(
        match_setup_fixture=match_setup_fixture,
        match_id=match_id,
        match_in_progress=match_in_progress,
    )
