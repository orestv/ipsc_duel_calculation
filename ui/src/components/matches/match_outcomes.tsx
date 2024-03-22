import React from "react";
import {useLoaderData} from "react-router-dom";
import {MatchDuel, MatchInProgress, MatchOutcomes} from "./models";
import {API_ROOT} from "../../storage";

interface MatchData {
    match: MatchInProgress
}


async function getMatchInProgress(matchId: string) {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}`
    )
    const matchInProgress = JSON.parse(await response.text())
    return matchInProgress
}

async function getMatchOutcomes(matchId: string) {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}/outcomes`
    )
    const matchOutcomes = JSON.parse(await response.text())
    return matchOutcomes
}

export async function loader({params}: any){
    const match = await getMatchInProgress(params.matchId)
    const outcomes = await getMatchOutcomes(params.matchId)
    return <>
        <h1>{match.name}</h1>
        <h2>{match.id}</h2>
    </>
}


export const MatchOutcomesComponent = () => useLoaderData() as JSX.Element