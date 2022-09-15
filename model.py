from __future__ import annotations

import dataclasses
import enum


class Category(str, enum.Enum):
    GENERAL = "Загальна"
    LADY = "Леді"


class Class(str, enum.Enum):
    STANDARD = "Стандарт"
    STANDARD_MANUAL = "Стандарт-мануал"
    MODIFIED = "Модифікований"
    OPEN = "Відкритий"


class Queue(str, enum.Enum):
    STANDARD_1 = "Стандарт 1"
    STANDARD_2 = "Стандарт 2"
    STANDARD_MANUAL = "Стандарт-мануал"
    MODIFIED = "Модифікований"
    OPEN = "Відкритий"
    Lady = "Леді"


class Range(enum.Enum):
    First = 1
    Second = 2


@dataclasses.dataclass
class Participant:
    number: str
    name: str
    status: str
    squad: int
    category: Category
    clazz: Class

    def __hash__(self):
        return hash(self.number)

    def __repr__(self):
        return self.name


@dataclasses.dataclass
class Duel:
    left: Participant
    right: Participant

    def __contains__(self, item):
        if not isinstance(item, Participant):
            return super(Duel, self).__contains__(item)
        return item == self.left or item == self.right

    def __repr__(self):
        return f"{self.left} - {self.right} ({self.left.clazz})"
