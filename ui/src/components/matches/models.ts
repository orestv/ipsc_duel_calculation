export interface MatchInProgress {
    id: string
    name: string
    participants: Participant[]
    duels: { [key: string]: MatchDuel[]}
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