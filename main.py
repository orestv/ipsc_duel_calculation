from __future__ import annotations

import csv
import random

from comp import QUEUE_REPEATS, RANGE_QUEUES, reoder_queue
from model import Category, Class, Range, Participant, Duel, Queue


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
