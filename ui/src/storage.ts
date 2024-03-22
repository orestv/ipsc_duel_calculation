import {MatchSetupRequest} from "./models";

const LOCAL_STORAGE_KEY = "participants-1";
export const API_ROOT = "/api";

export function saveMatchSetupToLocalStorage(participants: MatchSetupRequest) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(participants))
}

export function getMatchSetupFromLocalStorage() {
    const storedParticipants = localStorage.getItem(LOCAL_STORAGE_KEY);
    const participants: MatchSetupRequest | null = JSON.parse(storedParticipants);
    return participants;
}
