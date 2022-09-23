from __future__ import annotations

import dataclasses
import itertools

import model


@dataclasses.dataclass
class DuelOrderRank:
    duel: model.Duel

    delay_left: float
    delay_right: float

    pct_completed_left: float
    pct_completed_right: float

    def __repr__(self):
        return f"{self.duel} Delays: {self.delay_left:.2f}/{self.delay_right:.2f}; Completed: {self.pct_completed_left:.2f}/{self.pct_completed_right:.2f}"

    def is_valid(self) -> bool:
        for d in (self.delay_left, self.delay_right):
            if d is not None and d < 0.04:
                return False
        if abs(self.pct_completed_left - self.pct_completed_right) > 0.3:
            return False
        return True

    @property
    def sum_delay(self):
        return self.delay_left + self.delay_right

    @property
    def min_delay(self):
        return min(self.delay_left, self.delay_right)

    @property
    def max_delay(self):
        return max(self.delay_left, self.delay_right)

    @property
    def mean_delay(self):
        return mean(self.delay_left, self.delay_right)

    @property
    def delay_closeness(self):
        return abs(self.delay_left - self.delay_right)

    @property
    def mean_pct_complete(self):
        return mean(self.pct_completed_left, self.pct_completed_right)

    @property
    def min_pct_complete(self):
        return min(self.pct_completed_left, self.pct_completed_right)

    def __lt__(self, other: DuelOrderRank):
        return self.delay_left + self.delay_right > other.delay_left + other.delay_right and mean(self.pct_completed_left, self.pct_completed_right) > mean(other.pct_completed_left, other.pct_completed_right)


def mean(*args) -> float:
    return sum(
        arg**2 for arg in args
    )**0.5


def reorder_queue(queue: list[model.Duel]) -> list[model.Duel]:
    return queue
    schedule = queue[:1]
    queue = queue[1:]

    while queue:
        ranked_queue = order_queue(schedule, queue)
        preferred_duel = pick_preferred_duel(schedule, ranked_queue)
        queue.remove(preferred_duel)
        schedule.append(preferred_duel)

    return schedule


def order_queue(schedule: list[model.Duel], queue: list[model.Duel]) -> list[DuelOrderRank]:
    result = []

    duel_count = len(schedule) + len(queue)

    participants = set(itertools.chain(*schedule, *queue))

    percentages = {
        p: calculate_percentage_complete(p, schedule, queue)
        for p in participants
    }

    for queued_duel in queue:
        delay_left, delay_right = 1, 1

        for delay, scheduled_duel in enumerate(reversed(schedule)):
            normalized_delay = delay / duel_count
            if queued_duel.left in scheduled_duel:
                delay_left = min(delay_left, normalized_delay)
            if queued_duel.right in scheduled_duel:
                delay_right = min(delay_right, normalized_delay)

        pct_completed_left = percentages[queued_duel.left]
        pct_completed_right = percentages[queued_duel.right]

        ranking = DuelOrderRank(
            queued_duel, delay_left, delay_right, pct_completed_left,
            pct_completed_right
        )

        result.append(ranking)

    # result.sort()

    return result


def pick_preferred_duel(schedule: list[model.Duel], ranked_duels: list[DuelOrderRank]) -> model.Duel:
    ranked_duels.sort(key=lambda r: (-r.max_delay, ))
    # ranked_duels.sort(key=lambda r: (-r.max_delay, -total_ratios[r.duel.clazz]))

    # upcoming_duels = [d.duel for d in ranked_duels]
    # total_ratios = get_class_ratio(schedule + upcoming_duels)
    # scheduled_ratios = get_class_ratio(schedule)
    # upcoming_ratios = get_class_ratio(schedule)
    #
    #
    #
    # ratio_deltas = [
    #     (clazz, abs(scheduled_ratios.get(clazz, 0) - total_ratios[clazz]))
    #     for clazz, ratio in total_ratios.items()
    # ]
    # max_ratio_delta = max([r for _, r in ratio_deltas])
    # missed_classes = [c for c, r in ratio_deltas if r == max_ratio_delta]
    #
    # class_filtered_ranked_duels = list()
    # if missed_classes:
    #     class_filtered_ranked_duels = [
    #         d for d in ranked_duels
    #         if d.duel.clazz in missed_classes
    #     ]

    for candidate_duel in ranked_duels:
        if not candidate_duel.is_valid():
            continue

        return candidate_duel.duel
    return ranked_duels[0].duel

def calculate_percentage_complete(p: model.Participant, schedule: list[model.Duel], queue: list[model.Duel]) -> float:
    duels_participated = len(
        [duel for duel in schedule if p in duel]
    )
    duels_left = len(
        [duel for duel in queue if p in duel]
    )
    return duels_participated / (duels_participated + duels_left)

def get_class_ratio(duels: list[model.Duel]) -> dict[model.Class, float]:
    classes = {
        d.clazz for d in duels
    }

    result = {}
    for c in classes:
        ratio = len([d for d in duels if d.clazz == c]) / len(duels)
        result[c] = ratio
    return result
