import itertools
import operator

from duels.model import Class, Participant, Duel

NONCE = Participant("", Class.STANDARD)


def generate_duels(participants: list[Participant], repeat: bool) -> list[Duel]:
    if not participants:
        return list()
    participants = participants[:]
    # random.shuffle(participants)
    if len(participants) % 2 != 0:
        participants.append(NONCE)

    top, bottom = (
        participants[: len(participants) // 2],
        participants[len(participants) // 2 :],
    )

    result = []

    for idx in range(len(participants) - 1):
        tb = (top, bottom)
        d = list(zip(top, bottom))
        duels = [Duel(t, b) for t, b in zip(top, bottom)]
        result = result + duels
        top, bottom = _rotate(top, bottom)

    if repeat:
        result = result + [d.swapped() for d in result]
    else:
        # for non-repeat tournaments make sure everyone has more or less equal number of duels
        # where they're to the left and to the right
        first_participant = participants[0]
        first_participant_duels = [d for d in result if first_participant in d]
        remaining_duels, swap_duels = (
            first_participant_duels[::2],
            first_participant_duels[1::2],
        )
        for duel in swap_duels:
            idx = result.index(duel)
            result[idx] = duel.swapped()

    result = [d for d in result if NONCE not in d]

    result = _fix_disbalanced_pairs(result)
    return result


def merge_queues(queues: list[list[Duel]]) -> list[Duel]:
    percentages = [[(duel, idx / len(q)) for idx, duel in enumerate(q)] for q in queues]
    sorted_duels = sorted(
        itertools.chain.from_iterable(percentages), key=operator.itemgetter(1)
    )
    return [duel for duel, percentage in sorted_duels]

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


def _rotate(
    top: list[Participant], bottom: list[Participant]
) -> (list[Participant], list[Participant]):
    current = (top, bottom)
    result = ([top[0]] + [bottom[0]] + top[1 : len(top) - 1], bottom[1:] + [top[-1]])
    return result
