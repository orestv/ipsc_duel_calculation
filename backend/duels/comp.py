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

    # See: Circle Method at https://en.wikipedia.org/wiki/Round-robin_tournament
    if len(participants) % 2 != 0:
        participants.insert(0, NONCE)

    top, bottom = (
        participants[: len(participants) // 2],
        participants[len(participants) // 2 :],
    )

    result = []

    swap_left_right = False
    for idx in range(len(participants) - 1):
        duels = [Duel(t, b) for t, b in zip(top, bottom)]

        # In the Circle method, every participant will compete many times in a row
        # on the same duel side.
        # This piece swaps the sides every other time so that the participants switch
        # side every other duel.
        if swap_left_right:
            duels = [d.swapped() for d in duels]
        swap_left_right = not swap_left_right

        result = result + duels
        top, bottom = _rotate_clockwise(top, bottom)

    # Duplicate the tournament schedule as needed,
    # swapping the left/right pairs every time
    # to make sure everyone plays left/right more or less the same number of times.
    if times > 1:
        current_result = result
        for _ in range(times - 1):
            current_result = [d.swapped() for d in current_result]
            result = result + current_result

    result = [d for d in result if NONCE not in d]

    return result


def merge_queues(queues: list[list[Duel]]) -> list[Duel]:
    """Combine duel lists from multiple classes into a single queue.

    Ensures that the classes are merged more or less equally so that
    no class has all its duels in the beginning on in the end.
    """

    # how many duels in the class have already competed for each duel?
    percentages = [[(duel, idx / len(q)) for idx, duel in enumerate(q)] for q in queues]

    # merge the class queues so that all the classes
    # progress more or less equally fast.
    sorted_duels = sorted(
        itertools.chain.from_iterable(percentages), key=operator.itemgetter(1)
    )
    duels = [duel for duel, percentage in sorted_duels]
    duels = _fix_duels_in_row(duels)
    return duels


def _fix_duels_in_row(duels: list[Duel]) -> list[Duel]:
    """Ensure that no participants have two duels in a row."""

    for idx, (d1, d2) in enumerate(zip(duels[:-1], duels[1:])):
        if {d1.left.name, d1.right.name} & {d2.left.name, d2.right.name}:
            duels[idx - 1], duels[idx] = duels[idx], duels[idx - 1]

    for idx, (d1, d2) in enumerate(zip(duels[:-1], duels[1:])):
        if {d1.left.name, d1.right.name} & {d2.left.name, d2.right.name}:
            print(d1, d2)

    return duels


def _rotate_clockwise(
    top: list[Participant], bottom: list[Participant]
) -> (list[Participant], list[Participant]):
    """Fix the first item in place,
    rotate the rest clockwise.

    Convert:
      0 1 2 3
      4 5 6 7
    into
      0 4 1 2
      5 6 7 3

    See: Circle Method at https://en.wikipedia.org/wiki/Round-robin_tournament"""
    result = (
        [top[0]] + [bottom[0]] + top[1 : len(top) - 1],
        bottom[1:] + [top[-1]],
    )
    return result
