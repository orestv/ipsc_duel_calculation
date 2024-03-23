import {API_ROOT} from "../../storage";

import {DuelOutcome, MatchInProgress, MatchOutcomes, Participant, ParticipantVictories} from "./models";

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
    const matchOutcomes = JSON.parse(await response.text())
    return matchOutcomes
}

export async function fetchParticipantVictories(matchId: string): Promise<ParticipantVictories[]> {
    const response = await fetch(
        `${API_ROOT}/matches/${matchId}/victories`
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