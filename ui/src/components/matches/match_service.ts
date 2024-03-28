import {API_ROOT} from "../../storage";

import {
    CompletionStatus,
    DuelOutcome,
    MatchDuel,
    MatchInProgress,
    MatchOutcomes,
    Participant,
    ParticipantVictories
} from "./models";
import {MatchSetupRequest} from "../../models";

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
    const matchInProgress: MatchInProgress = JSON.parse(await response.text())
    const participantDictionary = getParticipantDictionary(matchInProgress.participants)
    for (const rng of Object.keys(matchInProgress.duels).map(Number)) {
        for (const duel of matchInProgress.duels[rng]) {
            duel.leftName = participantDictionary[duel.left].name
            duel.rightName = participantDictionary[duel.right].name
        }
    }
    matchInProgress.participantsDict = participantDictionary
    return matchInProgress
}

export async function fetchMatchOutcomes(matchId: string): Promise<MatchOutcomes> {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}/outcomes`
    )
    return JSON.parse(await response.text())
}

export async function fetchParticipantVictories(matchId: string): Promise<ParticipantVictories[]> {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}/victories`
    )
    return JSON.parse(await response.text())
}

export async function fetchMatchFromPracticarms(matchUrl: string): Promise<MatchSetupRequest> {
    const response = await fetch(
        `${API_ROOT}/duels/practicarms`,
        {
            method: "POST",
            body: JSON.stringify({"url": matchUrl})
        }
    )
    return JSON.parse(await response.text())
}

export async function recordOutcome(matchId: string, outcome: DuelOutcome) {
    await fetch(
        `${API_ROOT}/matches/${matchId}/duels/${outcome.duel_id}/outcomes`, {
            method: "POST",
            body: JSON.stringify(outcome),
        }
    )
}

export interface CompletionFilter {
    range?: number
    clazz?: string
}

export function getMatchCompletion(match: MatchInProgress, outcomes: MatchOutcomes, filter?: CompletionFilter): CompletionStatus {
    let rangeDuels: MatchDuel[] = []
    if (filter?.range) {
        rangeDuels = match.duels[filter.range] ?? []
    } else {
        for (const range of Object.keys(match.duels).map(Number)) {
            rangeDuels.push(...(match.duels[range] ?? []))
        }
    }


    if (filter?.clazz) {
        rangeDuels = rangeDuels.filter(
            (d) => {
                return d.clazz == filter.clazz
            }
        )
    }

    return getCompletionRate(
        rangeDuels,
        outcomes,
    )
}

export function getRangeCompletion(match: MatchInProgress, outcomes: MatchOutcomes, range: number): CompletionStatus {
    const duels = match.duels[range] ?? []
    return getCompletionRate(duels, outcomes)
}

function getCompletionRate(duels: MatchDuel[], outcomes: MatchOutcomes) {
    const duelIDs = duels.map((d) => {return d.id})
    const totalDuels = duels.length
    const mostRecentOutcomes = getMostRecentOutcomes(outcomes)
    const completedDuels = Object.keys(mostRecentOutcomes).filter(
        (duelId) => {
            return duelIDs.includes(duelId)
        }
    ).length
    return {
        completed: completedDuels,
        total: totalDuels
    }
}

function getParticipantDictionary(participants: Participant[]): { [key: string]: Participant } {
    return participants.reduce(
        (obj, participant) => {
            obj[participant.id] = participant
            return obj
        },
        {} as { [key: string]: Participant }
    )
}

export function getMostRecentOutcomes(outcomes: MatchOutcomes) {
    const mostRecentOutcomes: { [key: string]: DuelOutcome } = {}
    for (const duelId of Object.keys(outcomes.outcomes)) {
        const o = outcomes.outcomes[duelId]
        const last = o.reduce(
            (max, obj) => max.created_at > obj.created_at ? max : obj
        )
        mostRecentOutcomes[duelId] = last
    }
    return mostRecentOutcomes;
}