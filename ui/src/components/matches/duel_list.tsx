import React from "react";
import {API_ROOT} from "../../storage";
import {Button, Table} from "react-bootstrap";
import {FaGun} from "react-icons/fa6";
import {DuelOutcome, DuelVictory, MatchDuel, MatchInProgress, MatchOutcomes, Participant} from "./models";
import Container from "react-bootstrap/Container";
import {recordOutcome} from "./match_service";

export interface DuelListParams {
    matchId: string
    range: number
    participants: { [key: string]: Participant }
    duels: MatchDuel[]
    onOutcomeRecorded: () => void
}

export default function DuelList(params: DuelListParams) {
    // const duelRows = []
    // const duels = match.duels["1"]
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

    const duelRows = []
    for (const duel of duels) {
        duelRows.push(
            <tr key={duel.id}>
                <td>{duel.order}</td>
                <td>
                    <Button
                        className={'m-1'}
                        onClick={buildOutcomeHandler(duel.id, {left: true, right: false})}
                    ><FaGun/></Button>
                    {params.participants[duel.left].name}
                </td>
                <td>
                    <Button
                        className={'m-1'}
                        onClick={buildOutcomeHandler(duel.id, {left: false, right: true})}
                    ><FaGun/></Button>
                    {params.participants[duel.right].name}
                </td>
            </tr>
        )
    }

    return (
        <Container>
            <Table>
                <thead>

                </thead>
                <tbody>
                    {duelRows}
                </tbody>
            </Table>
        </Container>
    )
}