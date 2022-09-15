from __future__ import annotations

import dataclasses

from model import Queue, Range, Duel


@dataclasses.dataclass
class DuelOrderRank:
    duel: Duel

    def __lt__(self, other):
        raise NotImplementedError


@dataclasses.dataclass
class DuelOrderDelayForBoth(DuelOrderRank):
    left_delay: int
    right_delay: int

    def __lt__(self, other: DuelOrderDelayForBoth):
        return self.left_delay < other.left_delay


@dataclasses.dataclass
class DuelOrderPercentageCompleted(DuelOrderDelayForBoth):
    pct_completed_left: float
    pct_completed_right: float

    def __lt__(self, other: DuelOrderPercentageCompleted):
        return self.pct_completed_left < self.pct_completed_right


QUEUE_REPEATS = {
    Queue.STANDARD_1: False,
    Queue.STANDARD_2: False,
    Queue.STANDARD_MANUAL: False,
    Queue.MODIFIED: False,
    Queue.OPEN: True,
    Queue.Lady: True,
}

RANGE_QUEUES = {
    Range.First: [Queue.STANDARD_1, Queue.Lady, Queue.STANDARD_MANUAL, ],
    Range.Second: [Queue.STANDARD_2, Queue.MODIFIED, Queue.OPEN, ],
}


def reoder_queue(queue: list[Duel]) -> list[Duel]:
    schedule = queue[:1]
    queue = queue[1:]

    while queue:
        ranked_queue = order_queue(schedule, queue)
        preferred_duel = ranked_queue[-1].duel
        queue.remove(preferred_duel)
        schedule.append(preferred_duel)
        print(ranked_queue)

    return schedule


def order_queue(schedule: list[Duel], queue: list[Duel]) -> list[DuelOrderRank]:
    result = []

    MAXWEIGHT = 100

    for queued_duel in queue:
        delay_left, delay_right = MAXWEIGHT, MAXWEIGHT
        for delay, scheduled_duel in enumerate(reversed(schedule)):
            if delay_left == MAXWEIGHT and scheduled_duel.left in queued_duel:
                delay_left = delay
            if delay_right == MAXWEIGHT and scheduled_duel.right in queued_duel:
                delay_right = delay
        result.append(DuelOrderDelayForBoth(queued_duel, delay_left, delay_right))

    result.sort()

    return result


