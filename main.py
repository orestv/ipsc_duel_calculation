from __future__ import annotations

import csv
import os
import random

import pandas as pd

pd.options.plotting.backend = "plotly"
# import matplotlib.pyplot as plt

import model
from comp import reorder_queue
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
    # "single_tactics": {
    #     model.Range.First: [model.Queue.STANDARD_2, model.Queue.OPEN, model.Queue.STANDARD_MANUAL, ],
    #     model.Range.Second: [model.Queue.STANDARD_1, model.Queue.LADY, model.Queue.MODIFIED, ],
    # },
    "single_tactics_adapted": {
        model.Range.First: [model.Queue.STANDARD_2, model.Queue.MODIFIED, model.Queue.OPEN, ],
        model.Range.Second: [model.Queue.STANDARD, model.Queue.STANDARD_MANUAL, model.Queue.LADY, ],
    },
    "huge_standard": {
        model.Range.First: [model.Queue.STANDARD_2, model.Queue.STANDARD_MANUAL, model.Queue.MODIFIED,
                            model.Queue.OPEN, ],
        model.Range.Second: [model.Queue.STANDARD, model.Queue.LADY, ],
    },
    "huge_standard_everyone_once": {
        model.Range.First: [model.Queue.STANDARD_2, model.Queue.STANDARD_MANUAL, model.Queue.MODIFIED,
                            model.Queue.OPEN, ],
        model.Range.Second: [model.Queue.STANDARD, model.Queue.LADY, ],
    },
}

QUEUE_REPEATS = {
    model.Queue.STANDARD: False,
    model.Queue.STANDARD_2: False,
    model.Queue.STANDARD_MANUAL: False,
    model.Queue.MODIFIED: False,
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
        pairwise = 0
        for idx, left in enumerate(participants):
            for right in participants[idx + 1:]:
                duel = Duel(left, right)
                if pairwise % 2 == 0:
                    duel = Duel(right, left)
                pairwise += 1
                result.append(duel)
    # random.Random().shuffle(result)
    return result


def assert_pairs_valid(participants: list[Participant], variant_name: str, duels: list[Duel]) -> bool:
    MIN_DOWNTIME = 1
    MAX_DOWNTIME = 4

    duel_delays = get_participant_delays(duels)

    df = pd.DataFrame(
        [
            {
                "delay_left": delay[0],
                "delay_right": delay[1],
            }
            for delay, duel in duel_delays
        ],

        # {
        #     "delay_left": [delay[0] for delay, duel in duel_delays],
        #     "delay_right": [delay[1] for delay, duel in duel_delays],
        # }
    )
    print(variant_name)
    print(df.describe(include='all'))
    print("======")
    fig = df.plot(
        title=variant_name,
        kind="bar",
        # ylim=(-1, 25),
    )
    fig.show()
    # print(duel_delays)

    return True


def get_participant_delays(duels):
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
    return duel_delays


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
    swapper_names_1 = ["Волощук", "Корсун"]
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


def equalize_std(std_1: list[Participant], std_2: list[Participant]):
    n = "Степаняк Михайло"
    p = [x for x in std_2 if x.name == n][0]
    std_2.remove(p)
    std_1.append(p)


def build_queues(participants: list[Participant]) -> dict[Queue, list[Participant]]:
    men = [p for p in participants if p.category != Category.LADY]
    standard = [p for p in men if p.clazz == Class.STANDARD]

    # half = len(standard) // 2
    # standard_1, standard_2 = standard[:half], standard[half:]
    #
    # ensure_ladies_have_guns(standard_1, standard_2)
    # ensure_classes_not_fucked_up(standard_1, standard_2)
    # equalize_std(standard_1, standard_2)

    queues = {
        Queue.LADY: [p for p in participants if p.category == Category.LADY],
        Queue.MODIFIED: [p for p in men if p.clazz == Class.MODIFIED],
        Queue.OPEN: [p for p in men if p.clazz == Class.OPEN],
        Queue.STANDARD_MANUAL: [p for p in men if p.clazz == Class.STANDARD_MANUAL],
        Queue.STANDARD: standard,
    }

    return queues


def deliver_variant(range_queues, excel_writer: pd.ExcelWriter):
    for r, q in range_queues.items():
        delays = get_participant_delays(q)
        q_items = [
            {
                "number": idx + 1,
                "class": render_class(duel.clazz, duel.category),
                "left_name": duel.left.name,
                "right_name": duel.right.name,
                "left_delay": delays[idx][0][0],
                "right_delay": delays[idx][0][1]
            }
            for idx, duel in enumerate(q)
        ]
        df = pd.DataFrame(q_items)

        df.to_excel(excel_writer, sheet_name=f"Клас {r.value}")


def render_class(clazz: Class, category: Category) -> str:
    if clazz == Class.STANDARD_MANUAL:
        return "SM"
    elif clazz == Class.OPEN:
        return "O"
    elif clazz == Class.MODIFIED:
        return "T"
    elif clazz == Class.STANDARD:
        return "S" if category == Category.GENERAL else "SL"


def deliver_participants(participants: list[Participant], excel_writer: pd.ExcelWriter):
    df = pd.DataFrame(
        [
            {
                "name": p.name,
                "class": render_class(p.clazz, p.category),
            }
            for p in participants
        ]
    ).sort_values(["class", "name",]).set_index("class", drop=True)

    df["counts"] = df.groupby(["class", ]).count()
    df = df.reset_index().set_index(["class", "counts"])
    # cnt = df.groupby(["class", ]).count()

    df.to_excel(excel_writer, sheet_name="Учасники")


def main():
    participants = read_participants("participants.csv")
    queues = build_queues(participants)

    queue_duels = {
        queue_name: generate_duels(queue_participants, QUEUE_REPEATS[queue_name])
        for queue_name, queue_participants in queues.items()
    }
    queue_duels = {
        queue_name: reorder_queue(queue)
        for queue_name, queue in queue_duels.items()
    }

    variant_name = "basic"
    try:
        os.mkdir("out")
    except FileExistsError:
        pass
    target_dir = f"out/{variant_name}"
    try:
        os.mkdir(target_dir)
    except FileExistsError:
        pass
    excel_writer = pd.ExcelWriter(f"{target_dir}/pairs_{variant_name}.xlsx")

    deliver_participants(participants, excel_writer)
    deliver_variant(queue_duels, excel_writer)

    excel_writer.save()


# Press the green button in the gutter to run the script.

if __name__ == '__main__':
    main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
