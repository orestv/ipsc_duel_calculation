import React, {useEffect, useState} from "react";

import {Link, useLoaderData} from "react-router-dom";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Button, Card, Modal} from "react-bootstrap";
import {FaArrowLeft} from "react-icons/fa";
import {DuelOutcome, MatchDuel, MatchInProgress, MatchOutcomes, Participant, ParticipantVictories} from "./models";
import {fetchParticipantVictories} from "./match_service";

export async function loader({params}: any) {
    return <>
        <MatchResults matchId={params.matchId}/>
    </>
}

export const MatchResultsComponent = () => useLoaderData() as React.JSX.Element

interface MatchResultsParams {
    matchId: string
}

export function MatchResults(params: MatchResultsParams) {
    return (
        <Navbar>
            <Container>
                <Link to={`/matches/${params.matchId}`}>
                    <Button><FaArrowLeft/>&nbsp;Назад до матчу</Button>
                </Link>
            </Container>
        </Navbar>
    )
}

export interface MatchResultsModalParams {
    match: MatchInProgress
    outcomes: MatchOutcomes
    show: boolean
    onHide: () => void
}

export function MatchResultsModal(params: MatchResultsModalParams) {
    const defaultVictories = () => {return {} as {[key: string]: ParticipantVictories}}
    const [victories, setVictories] = useState(defaultVictories())
    useEffect(() => {
        (async () => {
            if (params.match.id == "") {
                return
            }
            const fetched = await fetchParticipantVictories(params.match.id)
            let result: {[key: string]: ParticipantVictories} = {}
            for (const v of fetched) {
                result[v.participant_id] = v
            }
            setVictories(result)
        })()
    }, [params.match.id, params.outcomes]);

    const victoriesRows = []
    for (const participantId of Object.keys(victories)) {
        victoriesRows.push(
            <Card key={participantId} className={"my-3"} style={{width: '100%'}}>
                <Card.Header>
                    <h3>{params.match.participantsDict[participantId].clazz}</h3>
                    <h3>{params.match.participantsDict[participantId].name}</h3>
                </Card.Header>
                <Card.Body>
                    {victories[participantId].victories}
                </Card.Body>
            </Card>
        )
    }

    return (
        <Modal show={params.show} onHide={params.onHide}>
            <Modal.Header closeButton>
                <Modal.Title>
                    Результати матчу "{params.match.name}"
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {victoriesRows}
            </Modal.Body>
        </Modal>
    )
}

interface DuelWithOutcome {
    duel: MatchDuel
    outcome?: DuelOutcome
}

interface RangeClassResultsParams {
    duelOutcomes: DuelWithOutcome[]
}

function RangeClassResults(params: RangeClassResultsParams) {
    return <></>
}