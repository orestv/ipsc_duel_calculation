import typing

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


class Duels(pydantic.BaseModel):
    ranges: dict[duels.model.Range, list[Duel]]
