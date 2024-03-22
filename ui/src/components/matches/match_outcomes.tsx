import React from "react";
import {useLoaderData} from "react-router-dom";
import {MatchDuel, MatchInProgress, MatchOutcomes, Participant} from "./models";
import {API_ROOT} from "../../storage";
import Container from "react-bootstrap/Container";
import {Table} from "react-bootstrap";
import {forEach} from "react-bootstrap/ElementChildren";

interface MatchData {
    match: MatchInProgress
}


async function getMatchInProgress(matchId: string): Promise<MatchInProgress> {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}`
    )
    const matchInProgress = JSON.parse(await response.text())
    return matchInProgress
}

async function getMatchOutcomes(matchId: string): Promise<MatchOutcomes> {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}/outcomes`
    )
    const matchOutcomes = JSON.parse(await response.text())
    return matchOutcomes
}

export async function loader({params}: any){
    const match = await getMatchInProgress(params.matchId)
    const outcomes = await getMatchOutcomes(params.matchId)

    const participants = match.participants.reduce(
        (obj, participant) => {
            obj[participant.id] = participant
            return obj
        },
        {} as {[key: string]: Participant}
    )

    const duelRows = []
    const duels = match.duels["1"]
    duels.sort((a, b) => {
        return a.order - b.order
    })

    for (const duel of duels) {
        duelRows.push(
            <tr key={duel.id}>
                <td>{duel.id}</td>
                <td>{participants[duel.left].name}</td>
                <td>{participants[duel.right].name}</td>
            </tr>
        )
    }

    return <>
        <h1>{match.name}</h1>
        <h2>{match.id}</h2>
        <Container>
            <Table>
                <thead>

                </thead>
                <tbody>
                    {duelRows}
                </tbody>
            </Table>
        </Container>
    </>
}


export const MatchOutcomesComponent = () => useLoaderData() as JSX.Element