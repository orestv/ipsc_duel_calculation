import {API_ROOT} from "../../storage";

import {MatchInProgress, MatchOutcomes} from "./models";

export async function fetchMatches(): Promise<MatchInProgress[]> {
    const response = await fetch(
        `${API_ROOT}/matches`, {
            method: "GET"
        }
    )
    const parsedJSON = JSON.parse(await response.text())
    const jsonWithDates = parsedJSON.map(
        (item: any) => {
            return {
                ...item,
                created_at: item.created_at ? new Date(item.created_at) : null,
            }
        }
    )
    jsonWithDates.sort((a: MatchInProgress, b: MatchInProgress) => {a.created_at < b.created_at}).reverse()
    return jsonWithDates
}

export async function deleteMatch(matchId: string) {
    await fetch(
        `${API_ROOT}/matches/${matchId}`, {
            method: "DELETE"
        }
    )
}

export async function fetchMatchInProgress(matchId: string): Promise<MatchInProgress> {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}`
    )
    const matchInProgress = JSON.parse(await response.text())
    return matchInProgress
}

async function fetchMatchOutcomes(matchId: string): Promise<MatchOutcomes> {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}/outcomes`
    )
    const matchOutcomes = JSON.parse(await response.text())
    return matchOutcomes
}