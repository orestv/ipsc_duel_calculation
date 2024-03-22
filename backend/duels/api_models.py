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


class MatchDuel(pydantic.BaseModel):
    id: uuid.UUID
    left: uuid.UUID
    right: uuid.UUID
    clazz: duels.model.Class


class MatchParticipant(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    clazz: duels.model.Class

    def __lt__(self, other: "MatchParticipant"):
        return (self.clazz, self.name) < (other.clazz, other.name)


class MatchInProgress(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    participants: list[MatchParticipant]
    participants_by_range: dict[duels.model.Range, list[uuid.UUID]]
    duels: dict[duels.model.Range, list[MatchDuel]]


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
