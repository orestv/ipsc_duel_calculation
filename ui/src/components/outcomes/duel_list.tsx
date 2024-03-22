import React from "react";
import {API_ROOT} from "../../storage";
import {Button} from "react-bootstrap";
import {FaGun} from "react-icons/fa6";
import {MatchInProgress, MatchOutcomes} from "../models";

export interface DuelListParams {
    matchId: string
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

export default function DuelList(params: DuelListParams) {
    // const participants = match.participants.reduce(
    //     (obj, participant) => {
    //         obj[participant.id] = participant
    //         return obj
    //     },
    //     {} as {[key: string]: Participant}
    // )
    //
    // const duelRows = []
    // const duels = match.duels["1"]
    // duels.sort((a, b) => {
    //     return a.order - b.order
    // })

    //  for (const duel of duels) {
    //     duelRows.push(
    //         <tr key={duel.id}>
    //             <td>{duel.id}</td>
    //             <td>
    //                 <Button className={'m-1'}><FaGun/></Button>
    //                 {participants[duel.left].name}
    //             </td>
    //             <td>
    //                 <Button className={'m-1'}><FaGun/></Button>
    //                 {participants[duel.right].name}
    //             </td>
    //         </tr>
    //     )
    // }

    return (
        <>Duel list be here</>
    )
}