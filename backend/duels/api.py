import logging
import tempfile
import uuid

import litestar
import litestar.exceptions
import litestar.background_tasks
import litestar.di
import litestar.exceptions
import litestar.response

import duels
import duels.comp
import duels.comp_excel
import duels.model
from duels.api_models import MatchSetup, Participant, Duel, Duels, MatchInProgress, MatchCreate, DuelOutcome, \
    ParticipantVictories, MatchOutcomes
from . import comp_excel
from . import inject
from .services import MatchService


class DuelsController(litestar.Controller):
    path = "/duels"

    dependencies = {
        "match_repository": litestar.di.Provide(inject.provide_match_repository),
        "results_repository": litestar.di.Provide(inject.provide_results_repository),
        "match_service": litestar.di.Provide(inject.provide_match_service),
    }

    @litestar.post(sync_to_thread=True)
    def get_duels(self, data: MatchSetup, match_service: MatchService) -> Duels:
        result = match_service.generate_duels(data)

        result = Duels(
            ranges={
                rng: [
                    Duel(
                        left=Participant(name=duel.left.name),
                        right=Participant(name=duel.right.name),
                        clazz=duel.clazz,
                    )
                    for duel in range_duels
                ]
                for rng, range_duels in result.items()
            }
        )
        return result

    @litestar.post("/excel", sync_to_thread=True)
    def get_duels_excel(self, data: MatchSetup, match_service: MatchService) -> litestar.response.File:
        range_duels = match_service.generate_duels(data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as f:
            pass

        path = f.name

        comp_excel.deliver_excel(range_duels, path)
        return litestar.response.File(path=path, filename="pairs.xlsx")


class MatchController(litestar.Controller):
    path = "/matches"
    dependencies = {
        "match_repository": litestar.di.Provide(inject.provide_match_repository),
        "results_repository": litestar.di.Provide(inject.provide_results_repository),
        "match_service": litestar.di.Provide(inject.provide_match_service),
    }

    @litestar.post()
    async def create_match(self, data: MatchCreate, match_service: MatchService) -> uuid.UUID:
        return await match_service.create_match(data)

    @litestar.get()
    async def get_matches(self, match_service: MatchService) -> list[MatchInProgress]:
        return await match_service.get_all_matches()

    @litestar.get("/{match_id:uuid}")
    async def get_match(self, match_id: uuid.UUID, match_service: MatchService) -> MatchInProgress:
        try:
            return await match_service.get_match(match_id)
        except KeyError:
            raise litestar.exceptions.NotFoundException()

    @litestar.delete("/{match_id:uuid}")
    async def delete_match(self, match_id: uuid.UUID, match_service: MatchService) -> None:
        await match_service.delete_match(match_id)

    @litestar.post("/{match_id:uuid}/duels/{duel_id:uuid}/outcomes")
    async def record_outcome(self, match_id: uuid.UUID, duel_id: uuid.UUID, data: DuelOutcome,
                             match_service: MatchService) -> litestar.Response[None]:
        await match_service.record_outcome(match_id, data)

        async def backup_match():
            await match_service.backup_match(match_id)

        return litestar.Response(
            None,
            background=litestar.background_tasks.BackgroundTask(backup_match),
        )

    @litestar.get("/{match_id:uuid}/duels/{duel_id:uuid}/outcomes")
    async def get_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID, match_service: MatchService) -> list[
        DuelOutcome]:
        return await match_service.get_duel_outcomes(match_id, duel_id)

    @litestar.get("{match_id:uuid}/outcomes")
    async def get_all_outcomes(self, match_id: uuid.UUID, match_service: MatchService) -> MatchOutcomes:
        return await match_service.get_match_outcomes(match_id)

    @litestar.get("/{match_id:uuid}/victories")
    async def get_victories(self, match_id: uuid.UUID, match_service: MatchService) -> list[ParticipantVictories]:
        return await match_service.get_victories(match_id)


def logging_exception_handler(_: litestar.Request, exc: Exception) -> litestar.Response:
    logging.exception(exc)
    # if isinstance(exc, litestar.exceptions.LitestarException):
    #     raise exc
    return litestar.Response(
        media_type=litestar.MediaType.JSON,
        content={"error": str(exc)},
        status_code=500,
    )


base_router = litestar.Router(
    path='/api',
    route_handlers=[DuelsController, MatchController],
)
app = litestar.Litestar(
    route_handlers=[base_router, ],
    # cors_config=CORSConfig(allow_origins=["http://localhost:4000"]),
    exception_handlers={Exception: logging_exception_handler},
)
