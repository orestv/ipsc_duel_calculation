import dataclasses
import uuid

import pytest
from faker import Faker
import litestar.status_codes
from litestar.testing import AsyncTestClient

import duels.model
from duels.api import app
from duels.api_models import Duels, MatchSetup, RangeSetup, ClassSetup, MatchCreate, MatchInProgress
from duels.model import Class, Range


async def test_match_empty(test_client: AsyncTestClient):
    response = await test_client.get(f"/matches/{uuid.uuid4()}")
    assert response.status_code == litestar.status_codes.HTTP_404_NOT_FOUND


async def test_empty_match_created(test_client: AsyncTestClient, faker: Faker):
    match = MatchCreate(
        name=faker.bs(),
        duels=Duels(
            ranges={
                "1": [],
                "2": [],
            }
        )
    )
    create_response = await test_client.post("/matches", content=match.json())
    assert create_response.status_code == litestar.status_codes.HTTP_201_CREATED
    match_id = create_response.json()
    get_response = await test_client.get(f"/matches/{match_id}")
    assert get_response.status_code == litestar.status_codes.HTTP_200_OK


@dataclasses.dataclass
class MatchSetupFixture:
    match_setup: MatchSetup
    participants: dict[duels.model.Class, list[str]]


@dataclasses.dataclass
class MatchOutcomeFixture:
    match_setup_fixture: MatchSetupFixture
    match_id: uuid.UUID


@pytest.fixture
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


@pytest.fixture
async def match_outcome_fixture(test_client, faker, match_setup_fixture) -> MatchOutcomeFixture:
    duels_response = await test_client.post("/duels", content=match_setup_fixture.match_setup.json())
    assert duels_response.status_code == litestar.status_codes.HTTP_201_CREATED
    duels = Duels.parse_obj(duels_response.json())

    match = MatchCreate(
        name=faker.bs(),
        duels=duels,
    )
    create_response = await test_client.post("/matches", content=match.json())
    assert create_response.status_code == litestar.status_codes.HTTP_201_CREATED
    match_id = uuid.UUID(create_response.json())
    return MatchOutcomeFixture(
        match_setup_fixture=match_setup_fixture,
        match_id=match_id,
    )

async def test_duels_generated(test_client: AsyncTestClient, match_setup_fixture: MatchSetupFixture, faker):
    match_setup = match_setup_fixture.match_setup
    duels_response = await test_client.post("/duels", content=match_setup.json())
    assert duels_response.status_code == litestar.status_codes.HTTP_201_CREATED
    duels = Duels.parse_obj(duels_response.json())

    match = MatchCreate(
        name=faker.bs(),
        duels=duels,
    )
    create_response = await test_client.post("/matches", content=match.json())
    assert create_response.status_code == litestar.status_codes.HTTP_201_CREATED
    match_id = create_response.json()

    get_response = await test_client.get(f"/matches/{match_id}")
    assert get_response.status_code == litestar.status_codes.HTTP_200_OK

    fetched_match = MatchInProgress.parse_obj(get_response.json())
    assert fetched_match.name == match.name

    fetched_participant_names = [
        p.name for p in fetched_match.participants
    ]
    assert sorted(fetched_participant_names) == sorted(match_setup_fixture.participants[Class.STANDARD])


async def test_record_outcome(match_outcome_fixture):
    print(match_outcome_fixture)