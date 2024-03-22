import dataclasses
import uuid

import pytest
from faker import Faker
import litestar.status_codes
from litestar.testing import AsyncTestClient

import duels.model
from duels.api import app
from duels.api_models import Duels, MatchSetup, RangeSetup, ClassSetup, MatchCreate, MatchInProgress, DuelOutcome, \
    OutcomeVictory
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
    match_in_progress: MatchInProgress


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

    match_response = await test_client.get(f"/matches/{match_id}")
    assert match_response.status_code == litestar.status_codes.HTTP_200_OK
    match_in_progress = MatchInProgress.parse_obj(match_response.json())
    return MatchOutcomeFixture(
        match_setup_fixture=match_setup_fixture,
        match_id=match_id,
        match_in_progress=match_in_progress,
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


async def test_record_outcome(test_client: AsyncTestClient, match_outcome_fixture: MatchOutcomeFixture):
    print(match_outcome_fixture)
    range_1_duels = match_outcome_fixture.match_in_progress.duels[Range.First]

    duel = range_1_duels[0]
    outcome = DuelOutcome(
        duel_id=duel.id,
        victory=OutcomeVictory(left=True),
        created_at=None,
    )
    outcome_url = f"/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
    outcome_create_response = await test_client.post(
        outcome_url,
        content=outcome.json(),
    )
    assert outcome_create_response.status_code == litestar.status_codes.HTTP_201_CREATED

    outcome_get_response = await test_client.get(outcome_url)
    assert outcome_get_response.status_code == litestar.status_codes.HTTP_200_OK
    fetched_outcomes = [DuelOutcome.parse_obj(x) for x in outcome_get_response.json()]
    assert len(fetched_outcomes) == 1

