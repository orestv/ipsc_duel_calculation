export interface MatchInProgress {
    id: string
    name: string
    participants: Participant[]
    duels: { [key: number]: MatchDuel[] }
    created_at: Date
}

export interface Participant {
    id: string
    name: string
    clazz: string
}

export interface MatchDuel {
    id: string
    order: number
    left: string
    right: string
    clazz: string
}

export interface MatchOutcomes {
    outcomes: { [key: string]: DuelOutcome[] }
}

export interface DuelOutcome {
    duel_id: string
    victory: DuelVictory
    dq?: DuelDQ
    created_at: Date
}

export interface DuelVictory {
    left: boolean
    right: boolean
}

export interface DuelDQ {
    left: boolean
    right: boolean
}