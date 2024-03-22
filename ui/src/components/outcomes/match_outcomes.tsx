import React, {useEffect, useState} from "react";
import {Link, useLoaderData} from "react-router-dom";
import {API_ROOT} from "../../storage";
import {MatchInProgress, MatchOutcomes, Participant} from "../models";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Button, Col, Row} from "react-bootstrap";
import DuelList from "./duel_list";

export async function loader({params}: any) {
    return <>
        <MatchReferee matchId={params.matchId}/>
    </>
}

export const MatchOutcomesComponent = () => useLoaderData() as JSX.Element

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


interface MatchRefereeParams {
    matchId: string
}

function getParticipantDictionary(participants: Participant[]): {[key: string]:Participant} {
    return participants.reduce(
        (obj, participant) => {
            obj[participant.id] = participant
            return obj
        },
        {} as {[key: string]: Participant}
    )
}

export function MatchReferee(params: MatchRefereeParams) {
    const defaultMatch = (): MatchInProgress => {
        return {created_at: undefined, duels: {}, id: "", name: "", participants: []}
    }
    const [match, setMatch] = useState(defaultMatch())
    useEffect(() => {
        (async () => {
            setMatch(await getMatchInProgress(params.matchId))
        })()
    }, []);

    const ranges = Object.keys(match.duels).map(Number)
    const [selectedRange, setSelectedRange] = useState(1)
    const rangeButtons = []
    for (const r of ranges) {
        rangeButtons.push(
                <Button variant={"secondary"} size={"lg"}
                        active={r == selectedRange}
                        key={r}
                        onClick={() => {
                            setSelectedRange(r)
                        }}
                >
                    Рубіж {r}
                </Button>
        )
    }

    console.log(match.duels)

    return <>
        <h1>Матч "{match.name}"</h1>
        <Navbar>
            <Container>
                {rangeButtons}
            </Container>
        </Navbar>
        <Container fluid>
            <Row>
                <DuelList
                    matchId={params.matchId}
                    range={selectedRange}
                    participants={getParticipantDictionary(match.participants)}
                    duels={match.duels[selectedRange] ?? []}
                />
            </Row>
        </Container>
    </>
}