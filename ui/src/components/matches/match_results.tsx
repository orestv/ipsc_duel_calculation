import React from "react";

import {Link, useLoaderData} from "react-router-dom";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Button, Modal} from "react-bootstrap";
import {FaArrowLeft} from "react-icons/fa";
import {DuelOutcome, MatchDuel, MatchInProgress, MatchOutcomes, Participant} from "./models";

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
    return (
        <Modal show={params.show} onHide={params.onHide}>
            <Modal.Header closeButton>
                <Modal.Title>
                    Результати матчу "{params.match.name}"
                </Modal.Title>
                <Modal.Body>

                </Modal.Body>
            </Modal.Header>
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