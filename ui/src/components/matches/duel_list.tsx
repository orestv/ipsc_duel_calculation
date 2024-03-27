import React from "react";
import {MatchDuel, MatchOutcomes} from "./models";
import {getMostRecentOutcomes} from "./match_service";
import DuelCard from "./duel_card";

export interface DuelListProps {
    matchId: string
    range: number
    duels: MatchDuel[]
    outcomes: MatchOutcomes
    isStale: boolean
    onOutcomeRecorded: () => void
}

export default function DuelList(props: DuelListProps) {
    const duels = props.duels
    duels.sort((a, b) => {
        return a.order - b.order
    })

    const mostRecentOutcomes = getMostRecentOutcomes(props.outcomes);
    const duelRows = []

    for (const duel of duels) {
        const outcome = mostRecentOutcomes[duel.id] ?? undefined
        duelRows.push(
            <DuelCard
                key={duel.id}
                matchId={props.matchId}
                duel={duel}
                outcome={outcome}
                isStale={props.isStale}
                onOutcomeRecorded={props.onOutcomeRecorded}
            />
        )
    }

    return (
        <>
            {duelRows}
        </>
    )
}