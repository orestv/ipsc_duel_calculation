from __future__ import annotations

import csv
import os
import random

import pandas as pd
import matplotlib.pyplot as plt

import model
from comp import reoder_queue
from model import Category, Class, Range, Participant, Duel, Queue

# RANGE_QUEUES = {
#     model.Range.First: [model.Queue.MODIFIED, model.Queue.STANDARD_MANUAL, ],
#     model.Range.Second: [model.Queue.STANDARD_1, model.Queue.STANDARD_2, model.Queue.LADY, model.Queue.OPEN, ],
# }
#
# # alternate 1
# RANGE_QUEUES = {
#     model.Range.First: [model.Queue.STANDARD_1, model.Queue.LADY, model.Queue.MODIFIED, ],
#     model.Range.Second: [model.Queue.STANDARD_2, model.Queue.OPEN, model.Queue.STANDARD_MANUAL, ],
# }
#
# # alternate 2
# RANGE_QUEUES = {
#     model.Range.First: [model.Queue.STANDARD_1, model.Queue.LADY, model.Queue.OPEN, ],
#     model.Range.Second: [model.Queue.STANDARD_2, model.Queue.MODIFIED, model.Queue.STANDARD_MANUAL, ],
# }

QUEUE_VARIANTS = {
    # "original": {
    #     model.Range.First: [model.Queue.MODIFIED, model.Queue.STANDARD_MANUAL, ],
    #     model.Range.Second: [model.Queue.STANDARD_1, model.Queue.STANDARD_2, model.Queue.LADY, model.Queue.OPEN, ],
    # },
    # "alternate_1": {
    #     model.Range.First: [model.Queue.STANDARD_2, model.Queue.OPEN, model.Queue.MODIFIED, ],
    #     model.Range.Second: [model.Queue.STANDARD_1, model.Queue.LADY,  model.Queue.STANDARD_MANUAL, ],
    # },
    "final": {
        model.Range.First: [model.Queue.STANDARD_2, model.Queue.OPEN,  model.Queue.STANDARD_MANUAL,],
        model.Range.Second: [model.Queue.STANDARD_1, model.Queue.LADY, model.Queue.MODIFIED, ],
    },
    # "alternate_4": {
    #     model.Range.First: [model.Queue.STANDARD_2, model.Queue.MODIFIED,  model.Queue.STANDARD_MANUAL, ],
    #     model.Range.Second: [model.Queue.STANDARD_1, model.Queue.LADY, model.Queue.OPEN,],
    # },
}

QUEUE_REPEATS = {
    model.Queue.STANDARD_1: False,
    model.Queue.STANDARD_2: False,
    model.Queue.STANDARD_MANUAL: False,
    model.Queue.MODIFIED: True,
    model.Queue.OPEN: True,
    model.Queue.LADY: True,
}


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


def assert_pairs_valid(participants: list[Participant], variant_name: str, duels: list[Duel]) -> bool:
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

    df = pd.DataFrame(
        {
            "delay_left": [delay[0] for delay, duel in duel_delays],
            "delay_right": [delay[0] for delay, duel in duel_delays],
        }
    )
    print(variant_name)
    print(df.describe(include='all'))
    print("======")
    df.plot(
        title=variant_name,
        kind="bar",
        ylim=(-1, 25),
    )
    plt.show()
    # print(duel_delays)

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


def ensure_ladies_have_guns(std_1: list[Participant], std_2: list[Participant]):
    husbands = ["Рогозін Олександр", "Шатєєв Олексій"]
    for name in husbands:
        for p in std_2:
            if p.name == name:
                p_for_swap = [
                    candidate for candidate in std_1 if candidate.name not in husbands
                ][0]
                std_2.remove(p)
                std_1.remove(p_for_swap)
                std_1.append(p)
                std_2.append(p_for_swap)
                break


def ensure_classes_not_fucked_up(std_1: list[Participant], std_2: list[Participant]):
    swapper_names_1 = ["Волощук", "Корсун" ]
    swapper_names_2 = ["Ситарський", "Кольченко", ]

    swappers_1 = [
        p
        for p in std_1
        for name in swapper_names_1
        if name in p.name
    ]
    swappers_2 = [
        p
        for p in std_2
        for name in swapper_names_2
        if name in p.name
    ]
    for left, right in zip(swappers_1, swappers_2):
        std_1.remove(left)
        std_2.append(left)

        std_2.remove(right)
        std_1.append(right)

def build_queues(participants: list[Participant]) -> dict[Queue, list[Participant]]:
    men = [p for p in participants if p.category != Category.LADY]
    standard = [p for p in men if p.clazz == Class.STANDARD]

    half = len(standard) // 2
    standard_1, standard_2 = standard[:half], standard[half:]

    ensure_ladies_have_guns(standard_1, standard_2)
    ensure_classes_not_fucked_up(standard_1, standard_2)

    queues = {
        Queue.LADY: [p for p in participants if p.category == Category.LADY],
        Queue.MODIFIED: [p for p in men if p.clazz == Class.MODIFIED],
        Queue.OPEN: [p for p in men if p.clazz == Class.OPEN],
        Queue.STANDARD_MANUAL: [p for p in men if p.clazz == Class.STANDARD_MANUAL],
        Queue.STANDARD_1: standard_1,
        Queue.STANDARD_2: standard_2,
    }
    return queues


def main():
    participants = read_participants("participants.csv")
    queues = build_queues(participants)

    queue_duels = {
        queue_name: generate_duels(queue_participants, QUEUE_REPEATS[queue_name])
        for queue_name, queue_participants in queues.items()
    }
    range_queues = {}
    try:
        os.mkdir("out")
    except FileExistsError:
        pass
    for variant_name, variant in QUEUE_VARIANTS.items():
        target_dir = f"out/{variant_name}"
        try:
            os.mkdir(target_dir)
        except FileExistsError:
            pass

        for r in Range:
            range_queues[r] = []
            for q_name in variant[r]:
                range_queues[r] += queue_duels[q_name]

        for r, q in range_queues.items():
            q = reoder_queue(q)
            q_items = [
                {
                    "number": idx + 1,
                    "class": render_class(duel.clazz, duel.category),
                    "left_name": duel.left.name,
                    "right_name": duel.right.name,
                }
                for idx, duel in enumerate(q)
            ]
            with open(f"{target_dir}/range_{r.value}.csv", "w") as f:
                writer = csv.DictWriter(f, q_items[0].keys())
                writer.writeheader()
                writer.writerows(q_items)
            name = f"{variant_name} - {r}"
            validity = assert_pairs_valid(participants, name, q)


def render_class(clazz: Class, category: Category) -> str:
    if clazz == Class.STANDARD_MANUAL:
        return "SM"
    elif clazz == Class.OPEN:
        return "O"
    elif clazz == Class.MODIFIED:
        return "T"
    elif clazz == Class.STANDARD:
        return "S" if category == Category.GENERAL else "SL"


# Press the green button in the gutter to run the script.

if __name__ == '__main__':
    main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
