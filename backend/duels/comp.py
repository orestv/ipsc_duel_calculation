import itertools
import operator

from duels.model import Class, Participant, Duel

NONCE = Participant("", Class.STANDARD)


def generate_duels(participants: list[Participant], times: int) -> list[Duel]:
    if not participants:
        return list()
    if times < 1:
        raise ValueError("The Times parameter must be >= 1.")
    participants = participants[:]
    # random.shuffle(participants)
    if len(participants) % 2 != 0:
        participants.insert(0, NONCE)
        # participants = [participants[0]] + [NONCE] + participants[1:]
        # participants.append(NONCE)

    top, bottom = (
        participants[: len(participants) // 2],
        participants[len(participants) // 2 :],
    )

    result = []

    swap_left_right = False
    for idx in range(len(participants) - 1):
        duels = [Duel(t, b) for t, b in zip(top, bottom)]

        if swap_left_right:
            duels = [d.swapped() for d in duels]
        swap_left_right = not swap_left_right

        result = result + duels
        top, bottom = _rotate_clockwise(top, bottom)

    if times > 1:
        current_result = result
        for _ in range(times - 1):
            current_result = [d.swapped() for d in current_result]
            result = result + current_result

    result = [d for d in result if NONCE not in d]

    # result = _fix_disbalanced_pairs(result)
    return result


def merge_queues(queues: list[list[Duel]]) -> list[Duel]:
    percentages = [[(duel, idx / len(q)) for idx, duel in enumerate(q)] for q in queues]
    sorted_duels = sorted(
        itertools.chain.from_iterable(percentages), key=operator.itemgetter(1)
    )
    duels = [duel for duel, percentage in sorted_duels]
    duels = _fix_duels_in_row(duels)
    return duels


def _fix_duels_in_row(duels: list[Duel]) -> list[Duel]:

    for idx, (d1, d2) in enumerate(zip(duels[:-1], duels[1:])):
        if {d1.left.name, d1.right.name} & {d2.left.name, d2.right.name}:
            duels[idx - 1], duels[idx] = duels[idx], duels[idx - 1]

    for idx, (d1, d2) in enumerate(zip(duels[:-1], duels[1:])):
        if {d1.left.name, d1.right.name} & {d2.left.name, d2.right.name}:
            print(d1, d2)

    return duels


# Todo: fix balancing
def _fix_disbalanced_pairs(duels: list[Duel]) -> list[Duel]:
    participants = {d.left for d in duels} | {d.right for d in duels}
    participants_leftright = []
    # Calculate number of left/right occurrences for each participant
    for p in participants:
        count_left = len([d for d in duels if d.left == p])
        count_right = len([d for d in duels if d.right == p])
        participants_leftright.append((count_left, count_right, p))

    # Find participants who have 2+ difference between their left and right duel sides
    disbalanced_participants = [
        (count_left, count_right, p)
        for count_left, count_right, p in participants_leftright
        if abs(count_left - count_right) > 1
    ]
    if not disbalanced_participants:
        return duels

    result = duels[:]
    disbalanced_participants.sort()
    half_length = len(disbalanced_participants) // 2
    db_left, db_right = (
        disbalanced_participants[:half_length],
        disbalanced_participants[half_length:],
    )
    for left, right in zip(db_left, db_right):
        pleft = left[2]
        pright = right[2]

        old_duel = Duel(pright, pleft)
        new_duel = Duel(pleft, pright)
        try:
            idx = result.index(old_duel)
            result[idx] = new_duel
        except ValueError:
            continue

    return result


def _rotate_clockwise(
    top: list[Participant], bottom: list[Participant]
) -> (list[Participant], list[Participant]):
    current = (top, bottom)
    result = (
        [top[0]] + [bottom[0]] + top[1 : len(top) - 1],
        bottom[1:] + [top[-1]],
    )
    # result = (
    #     [top[0]] + top[2:] + [bottom[-1]],
    #     [top[1]] + bottom[:len(bottom)-1],
    # )
    return result
