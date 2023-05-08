from __future__ import annotations

import dataclasses
import enum


class Category(str, enum.Enum):
    GENERAL = "G"
    LADY = "L"


class Class(str, enum.Enum):
    STANDARD = "S"
    STANDARD_MANUAL = "SM"
    MODIFIED = "M"
    OPEN = "O"
    STANDARD_LADY = "SL"


class Queue(str, enum.Enum):
    STANDARD_1 = "Стандарт 1"
    STANDARD_2 = "Стандарт 2"
    STANDARD_MANUAL = "Стандарт-мануал"
    MODIFIED = "Модифікований"
    OPEN = "Відкритий"
    LADY = "Леді"


class Range(str, enum.Enum):
    First = "1"
    Second = "2"


@dataclasses.dataclass
class Participant:
    name: str
    clazz: Class

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name


@dataclasses.dataclass
class Duel:
    left: Participant
    right: Participant

    def swapped(self) -> Duel:
        return Duel(self.right, self.left)

    def is_valid(self) -> bool:
        return (self.left.clazz, self.left.category) == (
            self.right.clazz,
            self.right.category,
        )

    @property
    def clazz(self) -> Class:
        return self.left.clazz

    def __contains__(self, item):
        # if not isinstance(item, Participant):
        #     return super(Duel, self).__contains__(item)
        return item == self.left or item == self.right

    def __repr__(self):
        return f"{self.left} - {self.right} ({self.left.clazz})"

    def __iter__(self):
        return iter([self.left, self.right])
