import React from "react";
import {API_ROOT} from "../../storage";
import {Button, Table} from "react-bootstrap";
import {FaGun} from "react-icons/fa6";
import {DuelOutcome, DuelVictory, MatchDuel, MatchInProgress, MatchOutcomes, Participant} from "./models";
import Container from "react-bootstrap/Container";
import {recordOutcome} from "./match_service";
import DuelCard from "./duel_card";

export interface DuelListParams {
    matchId: string
    range: number
    participants: { [key: string]: Participant }
    duels: MatchDuel[]
    outcomes: { [key: string]: DuelOutcome[] }
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

    const mostRecentOutcomes: {[key: string]: DuelOutcome} = {}
    for (const duelId of Object.keys(params.outcomes)) {
        const o = params.outcomes[duelId]
        const last = o.reduce(
            (max, obj) => max.created_at > obj.created_at ? max : obj
        )
        mostRecentOutcomes[duelId] = last
    }

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
                participants={params.participants}
                outcome={outcome}
                onOutcomeRecorded={params.onOutcomeRecorded}
            />
        )
    }

    // for (const duel of duels) {
    //     const outcome = mostRecentOutcomes[duel.id] ?? undefined
    //     const victoryLeft = outcome?.victory.left ?? false
    //     const victoryRight = outcome?.victory.right ?? false
    //     duelRows.push(
    //         <tr key={duel.id}>
    //             <td>{duel.order}</td>
    //             <td>
    //                 <Button
    //                     className={'m-1'}
    //                     onClick={buildOutcomeHandler(duel.id, {left: true, right: false})}
    //                 ><FaGun/></Button>
    //                 {participantName(params.participants[duel.left].name, victoryLeft)}
    //             </td>
    //             <td>
    //                 <Button
    //                     className={'m-1'}
    //                     onClick={buildOutcomeHandler(duel.id, {left: false, right: true})}
    //                 ><FaGun/></Button>
    //                 {participantName(params.participants[duel.right].name, victoryRight)}
    //             </td>
    //             <td>{new Date(outcome?.created_at)?.toLocaleTimeString('uk-UA', {hour12: false}) ?? ''}</td>
    //         </tr>
    //     )
    // }

    return (
        <Container>
            {duelRows}
            {/*<Table>*/}
            {/*    <thead>*/}

            {/*    </thead>*/}
            {/*    <tbody>*/}
            {/*        {duelRows}*/}
            {/*    </tbody>*/}
            {/*</Table>*/}
        </Container>
    )
}