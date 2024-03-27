import uuid

from faker import Faker
import litestar.status_codes
from litestar.testing import AsyncTestClient

from duels.api_models import Duels, MatchCreate, MatchInProgress, DuelOutcome, \
    OutcomeVictory, ParticipantVictories, OutcomeDQ, MatchDuel, MatchOutcomes
from duels.model import Class, Range
from duels.tests.conftest import MatchSetupFixture, MatchOutcomeFixture, match_setup_fixture, match_outcome_fixture


async def test_match_empty(test_client: AsyncTestClient):
    response = await test_client.get(f"/api/matches/{uuid.uuid4()}")
    assert response.status_code == litestar.status_codes.HTTP_404_NOT_FOUND, f"Error: {response.text}"\


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
    create_response = await test_client.post("/api/matches", content=match.json())
    assert create_response.status_code == litestar.status_codes.HTTP_201_CREATED
    match_id = create_response.json()
    get_response = await test_client.get(f"/api/matches/{match_id}")
    assert get_response.status_code == litestar.status_codes.HTTP_200_OK


async def test_duels_generated(test_client: AsyncTestClient, match_setup_fixture: MatchSetupFixture, faker):
    match_setup = match_setup_fixture.match_setup
    duels_response = await test_client.post("/api/duels", content=match_setup.json())
    assert duels_response.status_code == litestar.status_codes.HTTP_201_CREATED
    duels = Duels.parse_obj(duels_response.json())

    match = MatchCreate(
        name=faker.bs(),
        duels=duels,
    )
    create_response = await test_client.post("/api/matches", content=match.json())
    assert create_response.status_code == litestar.status_codes.HTTP_201_CREATED
    match_id = create_response.json()

    get_response = await test_client.get(f"/api/matches/{match_id}")
    assert get_response.status_code == litestar.status_codes.HTTP_200_OK, f"Failed to get response: {get_response.text}"

    fetched_match = MatchInProgress.parse_obj(get_response.json())
    assert fetched_match.name == match.name

    fetched_participant_names = [
        p.name for p in fetched_match.participants
    ]
    assert sorted(fetched_participant_names) == sorted(match_setup_fixture.participants[Class.STANDARD])


async def test_record_outcome(test_client: AsyncTestClient, match_outcome_fixture: MatchOutcomeFixture):
    range_1_duels = match_outcome_fixture.match_in_progress.duels[Range.First]

    duel = range_1_duels[0]
    outcome = DuelOutcome(
        duel_id=duel.id,
        victory=OutcomeVictory(left=True),
        created_at=None,
    )
    outcome_url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
    outcome_create_response = await test_client.post(
        outcome_url,
        content=outcome.json(),
    )
    assert outcome_create_response.status_code == litestar.status_codes.HTTP_201_CREATED

    outcome_get_response = await test_client.get(outcome_url)
    assert outcome_get_response.status_code == litestar.status_codes.HTTP_200_OK
    fetched_outcomes = [DuelOutcome.parse_obj(x) for x in outcome_get_response.json()]
    assert len(fetched_outcomes) == 1

    outcome_create_response = await test_client.post(
        outcome_url,
        content=outcome.json(),
    )
    assert outcome_create_response.status_code == litestar.status_codes.HTTP_201_CREATED

    outcome_get_response = await test_client.get(outcome_url)
    assert outcome_get_response.status_code == litestar.status_codes.HTTP_200_OK
    fetched_outcomes = [DuelOutcome.parse_obj(x) for x in outcome_get_response.json()]
    assert len(fetched_outcomes) == 2


async def test_record_reshoot(test_client: AsyncTestClient, match_outcome_fixture: MatchOutcomeFixture):
    range_1_duels = match_outcome_fixture.match_in_progress.duels[Range.First]
    duel = range_1_duels[0]
    outcome = DuelOutcome(
        duel_id=duel.id,
        reshoot=True,
        created_at=None,
    )
    outcome_url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
    outcome_create_response = await test_client.post(
        outcome_url,
        content=outcome.json(),
    )
    assert outcome_create_response.status_code == litestar.status_codes.HTTP_201_CREATED

    match_url = f"/api/matches/{match_outcome_fixture.match_id}"
    match_response = await test_client.get(match_url)
    assert match_response.status_code == litestar.status_codes.HTTP_200_OK
    fetched_match = MatchInProgress.parse_obj(match_response.json())
    fetched_range1_duels = fetched_match.duels[Range.First]
    assert len(fetched_range1_duels) == len(range_1_duels) + 1
    last_duel: MatchDuel = fetched_range1_duels[-1]
    assert (last_duel.left, last_duel.right) == (duel.left, duel.right)
    assert last_duel.order == len(fetched_range1_duels)


async def test_record_dq(test_client: AsyncTestClient, match_outcome_fixture: MatchOutcomeFixture):
    range_1_duels = match_outcome_fixture.match_in_progress.duels[Range.First]

    disqualified_participant_id = range_1_duels[0].left
    all_participant_duels = [
        duel
        for duel in range_1_duels
        if disqualified_participant_id in (duel.left, duel.right)
    ]
    success_duels = all_participant_duels[:2]
    disqualified_duel = all_participant_duels[2]

    for success_duel in success_duels:
        outcome = DuelOutcome(
            duel_id=success_duel.id,
            victory=OutcomeVictory(
                left=disqualified_participant_id == success_duel.left,
                right=disqualified_participant_id == success_duel.right,
            ),
            created_at=None,
        )
        await test_client.post(
            f"/api/matches/{match_outcome_fixture.match_id}/duels/{success_duel.id}/outcomes",
            content=outcome.json(),
        )

    outcome = DuelOutcome(
        duel_id=disqualified_duel.id,
        dq=OutcomeDQ(left=True),
        victory=OutcomeVictory(right=True),
        created_at=None,
    )
    outcome_url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{disqualified_duel.id}/outcomes"
    outcome_create_response = await test_client.post(
        outcome_url,
        content=outcome.json(),
    )
    assert outcome_create_response.status_code == litestar.status_codes.HTTP_201_CREATED

    outcome_url = f"/api/matches/{match_outcome_fixture.match_id}/outcomes"
    outcome_response = await test_client.get(outcome_url)
    assert outcome_response.status_code == litestar.status_codes.HTTP_200_OK
    outcome = MatchOutcomes.parse_obj(outcome_response.json())

    expected_loss_duels = [
        d for d in all_participant_duels
        if d.id not in [dd.id for dd in success_duels] + [disqualified_duel.id]
    ]
    for lost_duel in expected_loss_duels:
        assert lost_duel.id in outcome.outcomes
        duel_outcome = outcome.outcomes[lost_duel.id][-1]
        assert duel_outcome.dummy
        assert duel_outcome.victory == OutcomeVictory(
            left=lost_duel.left != disqualified_participant_id,
            right=lost_duel.right != disqualified_participant_id,
        )


async def test_calculate_victories(test_client: AsyncTestClient, match_outcome_fixture: MatchOutcomeFixture):
    victor = match_outcome_fixture.match_in_progress.participants[0]
    victor_duels = [
        d
        for rng, duels in match_outcome_fixture.match_in_progress.duels.items()
        for d in duels
        if victor.id in (d.left, d.right)
    ]
    assert len(victor_duels) == 18

    for duel in victor_duels:
        victory = OutcomeVictory(
            left=duel.left == victor.id,
            right=duel.right == victor.id
        )
        outcome = DuelOutcome(
            duel_id=duel.id,
            victory=victory,
            created_at=None,
        )
        url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
        response = await test_client.post(url, content=outcome.json())
        assert response.status_code == litestar.status_codes.HTTP_201_CREATED

    victories_response = await test_client.get(f"/api/matches/{match_outcome_fixture.match_id}/victories")
    assert victories_response.status_code == litestar.status_codes.HTTP_200_OK
    victories = [
        ParticipantVictories.parse_obj(v) for v in victories_response.json()
    ]
    assert len(victories) == len(match_outcome_fixture.match_in_progress.participants)
    fetched_victor = [v for v in victories if v.participant_id == victor.id][0]
    assert fetched_victor.victories == 18


async def test_calculate_dq(test_client: AsyncTestClient, match_outcome_fixture: MatchOutcomeFixture):
    victor = match_outcome_fixture.match_in_progress.participants[0]
    victor_duels = [
        d
        for rng, duels in match_outcome_fixture.match_in_progress.duels.items()
        for d in duels
        if victor.id in (d.left, d.right)
    ]
    assert len(victor_duels) == 18

    for duel in victor_duels:
        victory = OutcomeVictory(
            left=duel.left == victor.id,
            right=duel.right == victor.id
        )
        outcome = DuelOutcome(
            duel_id=duel.id,
            victory=victory,
            created_at=None,
        )
        url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
        response = await test_client.post(url, content=outcome.json())
        assert response.status_code == litestar.status_codes.HTTP_201_CREATED

    duel = victor_duels[-3]
    victory = OutcomeVictory(
        left=duel.left != victor.id,
        right=duel.right != victor.id,
    )
    dq = OutcomeDQ(
        left=duel.left == victor.id,
        right=duel.right == victor.id,
    )
    outcome = DuelOutcome(
        duel_id=duel.id,
        victory=victory,
        dq=dq,
        created_at=None,
    )
    url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
    response = await test_client.post(url, content=outcome.json())
    assert response.status_code == litestar.status_codes.HTTP_201_CREATED

    victories_response = await test_client.get(f"/api/matches/{match_outcome_fixture.match_id}/victories")
    assert victories_response.status_code == litestar.status_codes.HTTP_200_OK
    victories = [
        ParticipantVictories.parse_obj(v) for v in victories_response.json()
    ]
    assert len(victories) == len(match_outcome_fixture.match_in_progress.participants)
    fetched_victor = [v for v in victories if v.participant_id == victor.id][0]
    assert fetched_victor.victories == 0
    assert fetched_victor.dq == True


async def test_calculate_overwritten_victories(test_client: AsyncTestClient,
                                               match_outcome_fixture: MatchOutcomeFixture):
    victor = match_outcome_fixture.match_in_progress.participants[0]
    victor_duels = [
        d
        for rng, duels in match_outcome_fixture.match_in_progress.duels.items()
        for d in duels
        if victor.id in (d.left, d.right)
    ]
    assert len(victor_duels) == 18

    for duel in victor_duels:
        victory = OutcomeVictory(
            left=duel.left != victor.id,
            right=duel.right != victor.id
        )
        outcome = DuelOutcome(
            duel_id=duel.id,
            victory=victory,
            created_at=None,
        )
        url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
        response = await test_client.post(url, content=outcome.json())
        assert response.status_code == litestar.status_codes.HTTP_201_CREATED

    for duel in victor_duels:
        victory = OutcomeVictory(
            left=duel.left == victor.id,
            right=duel.right == victor.id
        )
        outcome = DuelOutcome(
            duel_id=duel.id,
            victory=victory,
            created_at=None,
        )
        url = f"/api/matches/{match_outcome_fixture.match_id}/duels/{duel.id}/outcomes"
        response = await test_client.post(url, content=outcome.json())
        assert response.status_code == litestar.status_codes.HTTP_201_CREATED

    victories_response = await test_client.get(f"/api/matches/{match_outcome_fixture.match_id}/victories")
    assert victories_response.status_code == litestar.status_codes.HTTP_200_OK
    victories = [
        ParticipantVictories.parse_obj(v) for v in victories_response.json()
    ]
    assert len(victories) == len(match_outcome_fixture.match_in_progress.participants)
    fetched_victor = [v for v in victories if v.participant_id == victor.id][0]
    assert fetched_victor.victories == 18
