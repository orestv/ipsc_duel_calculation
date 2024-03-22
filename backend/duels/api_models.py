import datetime
import typing
import uuid

import pydantic

import duels.model


class ClassSetup(pydantic.BaseModel):
    participants: list[str]
    times: int


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


class MatchDuel(Duel):
    id: uuid.UUID


class MatchDuels(pydantic.BaseModel):
    ranges: dict[duels.model.Range, list[MatchDuel]]


class Duels(pydantic.BaseModel):
    ranges: dict[duels.model.Range, list[Duel]]


class MatchCreate(pydantic.BaseModel):
    name: str
    duels: Duels


class OutcomeDQ(pydantic.BaseModel):
    left: bool = False
    right: bool = False


class OutcomeVictory(pydantic.BaseModel):
    left: bool = False
    right: bool = False


class DuelOutcome(pydantic.BaseModel):
    duel: MatchDuel
    dq: OutcomeDQ
    created_at: typing.Optional[datetime.datetime]
