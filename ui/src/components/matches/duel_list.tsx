import React from "react";
import {DuelOutcome, DuelVictory, MatchDuel, MatchOutcomes} from "./models";
import Container from "react-bootstrap/Container";
import {getMostRecentOutcomes, recordOutcome} from "./match_service";
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

    const buildOutcomeHandler = (duelId: string, victory: DuelVictory) => {
        return async () => {
            await handleOutcome(duelId, victory)
        }
    }
    const handleOutcome = async (duelId: string, victory: DuelVictory) => {
        const outcome: DuelOutcome = {
            duel_id: duelId,
            victory: victory,
        }
        await recordOutcome(params.matchId, outcome)
        params.onOutcomeRecorded()
    }

    const mostRecentOutcomes = getMostRecentOutcomes(params.outcomes);

    const participantName = (pName: string, victory: boolean) => {
        return <p style={{fontWeight: victory ? "bold" : "normal"}}>{pName}</p>
    }

    const duelRows = []

    for (const duel of duels) {
        const outcome = mostRecentOutcomes[duel.id] ?? undefined
        duelRows.push(
            <DuelCard
                matchId={params.matchId}
                duel={duel}
                outcome={outcome}
                onOutcomeRecorded={params.onOutcomeRecorded}
            />
        )
    }

    return (
        <Container>
            {duelRows}
        </Container>
    )
}