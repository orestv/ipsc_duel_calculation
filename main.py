import csv
import dataclasses
import enum
import random
import sys


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


QUEUE_REPEATS = {
    Queue.STANDARD_1: False,
    Queue.STANDARD_2: False,
    Queue.STANDARD_MANUAL: False,
    Queue.MODIFIED: False,
    Queue.OPEN: True,
    Queue.Lady: True,
}


class Range(enum.Enum):
    First = 1
    Second = 2


RANGE_QUEUES = {
    Range.First: [Queue.STANDARD_1, Queue.Lady, Queue.STANDARD_MANUAL, ],
    Range.Second: [Queue.STANDARD_2, Queue.MODIFIED, Queue.OPEN, ],
}


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


def generate_duels(participants: list[Participant], repeat: bool) -> list[Duel]:
    result = []
    if repeat:
        result = [
            Duel(p1, p2)
            for p1 in participants
            for p2 in participants
            if p1 != p2
        ]
    else:
        for idx, left in enumerate(participants):
            for right in participants[idx + 1:]:
                result.append(Duel(left, right))
    # random.Random().shuffle(result)
    return result


def assert_pairs_valid(participants: list[Participant], duels: list[Duel]) -> bool:
    MIN_DOWNTIME = 1
    MAX_DOWNTIME = 4

    duel_delays = []
    for idx, duel in enumerate(duels):
        if idx == 0:
            duel_delays.append(((None, None), duel))
            continue
        delay_left = None
        delay_right = None
        delay = None
        for delay, prev_duel in enumerate(reversed(duels[:idx])):
            if delay_left is None and duel.left in prev_duel:
                delay_left = delay
            if delay_right is None and duel.right in prev_duel:
                delay_right = delay
        duel_delays.append(((delay_left, delay_right), duel))

    print(duel_delays)

    return True


def read_participants(path: str) -> list[Participant]:
    result = []
    with open(path) as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            for cat in Category:
                if row["category"] == cat.value:
                    row["category"] = cat
                    break
            else:
                raise ValueError(f"No category found for {row}")
            for c in Class:
                if row["clazz"] == c.value:
                    row["clazz"] = c
                    break
            else:
                raise ValueError(f"No class found for {row}")
            p = Participant(**row)
            result.append(p)
    return result


def build_queues(participants: list[Participant]) -> dict[Queue, list[Participant]]:
    rand = random.Random()
    men = [p for p in participants if p.category != Category.LADY]
    standard = [p for p in men if p.clazz == Class.STANDARD]
    random.shuffle(standard)
    half = len(standard) // 2
    standard_1, standard_2 = standard[:half], standard[half:]

    queues = {
        Queue.Lady: [p for p in participants if p.category == Category.LADY],
        Queue.MODIFIED: [p for p in men if p.clazz == Class.MODIFIED],
        Queue.OPEN: [p for p in men if p.clazz == Class.OPEN],
        Queue.STANDARD_MANUAL: [p for p in men if p.clazz == Class.STANDARD_MANUAL],
        Queue.STANDARD_1: standard_1,
        Queue.STANDARD_2: standard_2,
    }
    return queues


def reoder_queue(queue: list[Duel]) -> list[Duel]:
    schedule = queue[:1]
    queue = queue[1:]

    while queue:
        delays = calculate_delays(schedule, queue)
        _, preferred_duel = delays[-1]
        queue.remove(preferred_duel)
        schedule.append(preferred_duel)
        print(delays)

    return schedule


def calculate_delays(schedule: list[Duel], queue: list[Duel]) -> list[tuple[int, Duel]]:
    result = []

    MAXWEIGHT = 100

    for queued_duel in queue:
        delay_left, delay_right = MAXWEIGHT, MAXWEIGHT
        for delay, scheduled_duel in enumerate(reversed(schedule)):
            if delay_left == MAXWEIGHT and scheduled_duel.left in queued_duel:
                delay_left = delay
            if delay_right == MAXWEIGHT and scheduled_duel.right in queued_duel:
                delay_right = delay
        effective_delay = delay_left + delay_right
        effective_delay = (delay_left + delay_right, -abs(delay_left - delay_right))
        effective_delay = max(delay_left, delay_right) - abs(delay_left - delay_right)
        # effective_delay = max(delay_left, delay_right) - min(delay_left, delay_right)
        result.append((effective_delay, queued_duel))
        #     if {queued_duel.left, queued_duel.right} & {scheduled_duel.left, scheduled_duel.right}:
        #         result.append((delay, queued_duel))
        #         break
        # else:
        #     result.append((sys.maxsize, queued_duel))
    last_scheduled_duel = schedule[-1]

    random.Random().shuffle(result)
    # result.sort(key=lambda r: (r[0], r[1].left.clazz != last_scheduled_duel.left.clazz and r[1].left.category != last_scheduled_duel.left.category))
    result.sort(key=lambda r: r[0])

    return result


def main():
    participants = read_participants("participants.csv")
    print(len(participants))
    queues = build_queues(participants)
    for q, p in queues.items():
        print(f"{q}: {len(p)} {p}")

    queue_duels = {
        queue_name: generate_duels(queue_participants, QUEUE_REPEATS[queue_name])
        for queue_name, queue_participants in queues.items()
    }
    range_queues = {}
    for r in Range:
        range_queues[r] = []
        for q_name in RANGE_QUEUES[r]:
            range_queues[r] += queue_duels[q_name]
    for r, q in range_queues.items():
        q = reoder_queue(q)
        print(f"{r}, {len(q)}, {q}")
        validity = assert_pairs_valid(participants, q)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
