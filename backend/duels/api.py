import logging
import tempfile
import traceback

import pydantic
import litestar
import litestar.exceptions
from litestar.config.cors import CORSConfig
from litestar.response_containers import File
import pandas as pd

import duels
import duels.model
import duels.comp
import duels.comp_excel
from duels.comp_excel import deliver_participants


class ClassSetup(pydantic.BaseModel):
    participants: list[str]
    twice: bool


class RangeSetup(pydantic.BaseModel):
    classes: dict[duels.model.Class, ClassSetup]


class MatchSetup(pydantic.BaseModel):
    ranges: dict[duels.model.Range, RangeSetup]


class Participant(pydantic.BaseModel):
    name: str


class Duel(pydantic.BaseModel):
    left: Participant
    right: Participant
    clazz: duels.model.Class


class Duels(pydantic.BaseModel):
    ranges: dict[duels.model.Range, list[Duel]]


class DuelsController(litestar.Controller):
    path = "/duels"

    @litestar.post()
    def get_duels(self, data: MatchSetup) -> Duels:
        result = self._generate_duels(data)

        result = Duels(ranges={
            rng: [
                Duel(
                    left=Participant(name=duel.left.name),
                    right=Participant(name=duel.right.name),
                    clazz=duel.clazz,
                )
                for duel in range_duels
            ]
            for rng, range_duels in result.items()
        })
        return result

    @litestar.post("/excel")
    def get_duels_excel(self, data: MatchSetup) -> File:
        range_duels = self._generate_duels(data)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello world!\n")

        # excel_writer = pd.ExcelWriter("/tmp/out.xlsx")
        #
        # deliver_participants()
        #
        # duels.comp_excel.deliver_participants(participants, excel_writer)
        #
        # for range, duels in range_duels.items():
        #     range_participants = set(itertools.chain(*duels))
        #     deliver_range_lists(range, range_participants, excel_writer)
        #
        # deliver_standard_groups(
        #     queues[Queue.STANDARD_1], queues[Queue.STANDARD_2], excel_writer
        # )
        #
        # for range, duels in range_duels.items():
        #     deliver_range_pairs(range, duels, excel_writer)
        #
        # deliver_sorted_pairs(range_duels, excel_writer)
        # equalize_column_width(excel_writer)
        #
        # excel_writer.save()
        return File(path=f.name, filename="today.txt")

    def _generate_duels(self, match_setup: MatchSetup):
        result = {
            rng: [
                duels.comp.generate_duels(
                    [
                        duels.model.Participant(name, clazz)
                        for name in clazz_setup.participants
                    ],
                    clazz_setup.twice,
                )
                for clazz, clazz_setup in range_setup.classes.items()
            ]
            for rng, range_setup in match_setup.ranges.items()
        }
        result = {
            rng: duels.comp.merge_queues(d)
            for rng, d in result.items()
        }
        return result


def logging_exception_handler(_: litestar.Request, exc: Exception) -> litestar.Response:
    logging.exception(exc)
    return litestar.Response(
        media_type=litestar.MediaType.JSON,
        content={"error": str(exc)},
        status_code=500,
    )


app = litestar.Litestar(
    route_handlers=[DuelsController],
    cors_config=CORSConfig(allow_origins=["http://localhost:4000"]),
    exception_handlers={Exception: logging_exception_handler},
)
