import React from "react";
import {API_ROOT} from "../../storage";
import {Button, Table} from "react-bootstrap";
import {FaGun} from "react-icons/fa6";
import {MatchDuel, MatchInProgress, MatchOutcomes, Participant} from "../models";
import Container from "react-bootstrap/Container";

export interface DuelListParams {
    matchId: string
    range: number
    participants: { [key: string]: Participant }
    duels: MatchDuel[]
}

export default function DuelList(params: DuelListParams) {
    console.log("Params: ", params.duels)
    // const duelRows = []
    // const duels = match.duels["1"]
    const duels = params.duels
    duels.sort((a, b) => {
        return a.order - b.order
    })

    const duelRows = []
    for (const duel of duels) {
        duelRows.push(
            <tr key={duel.id}>
                <td>{duel.order}</td>
                <td>
                    <Button className={'m-1'}><FaGun/></Button>
                    {params.participants[duel.left].name}
                </td>
                <td>
                    <Button className={'m-1'}><FaGun/></Button>
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