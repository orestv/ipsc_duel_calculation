export interface ParticipantListRequest {
    ranges: { [key: string]: RangeRequest };
}

export interface RangeRequest {
    classes: {  [key: string] : ClassParticipantList };
}

export interface ClassParticipantList {
    participants: string[];
    twice:        boolean;
}

export interface Match {
    ranges: { [key: string] : Duel[]}
}

export interface Duel {
    left: Participant
    right: Participant
    clazz: string
}

export interface Participant {
    name: string
}