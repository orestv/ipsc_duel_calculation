import React from "react";
import {MatchDuel, MatchOutcomes} from "./models";
import {getMostRecentOutcomes} from "./match_service";
import DuelCard from "./duel_card";

export interface DuelListParams {
    matchId: string
    range: number
    duels: MatchDuel[]
    outcomes: MatchOutcomes
    onOutcomeRecorded: () => void
}

export default function DuelList(params: DuelListParams) {
    const duels = params.duels
    duels.sort((a, b) => {
        return a.order - b.order
    })

    const mostRecentOutcomes = getMostRecentOutcomes(params.outcomes);
    const duelRows = []

    for (const duel of duels) {
        const outcome = mostRecentOutcomes[duel.id] ?? undefined
        duelRows.push(
            <DuelCard
                key={duel.id}
                matchId={params.matchId}
                duel={duel}
                outcome={outcome}
                onOutcomeRecorded={params.onOutcomeRecorded}
            />
        )
    }

    return (
        <>
            {duelRows}
        </>
    )
}