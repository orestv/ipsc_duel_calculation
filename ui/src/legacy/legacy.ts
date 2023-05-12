import {ClassParticipantList, Match, ParticipantListRequest, RangeRequest} from "../models";
import * as $ from "jquery";

const LOCAL_STORAGE_KEY = "participants-1";
const API_ROOT = "http://localhost:5000";
const CLASSES = ["S", "SL", "SM", "M", "O"];
const RANGES = ["1", "2"];

export function saveToLocalStorage() {
    const participants = buildParticipantRequest();
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(participants))
}

export function loadFromLocalStorage() {
    const storedParticipants = localStorage.getItem(LOCAL_STORAGE_KEY);
    const participants: ParticipantListRequest | null = JSON.parse(storedParticipants);
    if (participants == null) {
        return;
    }
    for (const [rangeName, range] of Object.entries(participants.ranges)) {
        for (const [clazzName, clazz] of Object.entries(range.classes)) {
            const input = getInput(rangeName, clazzName);
            const value = clazz.participants.join("\n");
            input.val(value);
        }
    }
    generatePairs();
}

export function generatePairs() {
    const request = buildParticipantRequest();
    $.post(`${API_ROOT}/duels`,
        JSON.stringify(request),
        function (response) {
            renderMatch(response as Match)
        }
    );
}

function renderMatch(match: Match) {
    console.log(match)
    $("#container-result").show();
    $("#tbodyRange1").empty();
    $("#tbodyRange2").empty();

    for (const range of RANGES) {
        const duels = match.ranges[range]
        const tbodyQuery = `#tbodyRange${range}`
        for (const duel of duels) {
            const rowHtml = `<tr><td>${duel.left.name}</td><td>${duel.right.name}</td><td>${duel.clazz}</td></tr>`
            $(tbodyQuery).append(rowHtml);
        }
        const countBadgeQuery = `#spDuelCount${range}`
        $(countBadgeQuery).text(duels.length)
    }
}

function buildParticipantRequest(): ParticipantListRequest {
    const ranges = ["1", "2"]

    let result: ParticipantListRequest = {
        ranges: {}
    };
    for (const range of RANGES) {
        result.ranges[range] = getRangeClasses(range);
    }
    return result
}

function getRangeClasses(range: string): RangeRequest {
    let result: RangeRequest = {
        classes: {}
    }
    for (const clazz of CLASSES) {
        const classParticipants = getClassParticipants(range, clazz);
        if (classParticipants.participants.length > 0) {
            result.classes[clazz] = classParticipants
        }
    }
    return result
}

function getClassParticipants(range: string, clazz: string): ClassParticipantList {
    const participants = getEnteredParticipantList(range, clazz);
    const twice = false;
    return {participants, twice}
}

function getInputId(range: string, clazz: string): string {
    return `part-${clazz}-r${range}`;
}

function getInputQuery(range: string, clazz: string): string {
    const inputId = getInputId(range, clazz);
    return `#${inputId}`
}

function getInput(range: string, clazz: string): JQuery<HTMLElement> {
    return $(getInputQuery(range, clazz));
}

function getEnteredParticipantList(range: string, clazz: string): string[] {
    const input = getInput(range, clazz)
    const val = input.val() as string;
    if (val.length == 0) {
        return [];
    }
    let rows = val.split("\n")
    rows = rows.filter((i) => i.length > 0)
    return rows
}
