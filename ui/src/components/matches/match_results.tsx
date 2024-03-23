import React, {useEffect, useState} from "react";

import {Link, useLoaderData} from "react-router-dom";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Badge, Button, Modal, Table} from "react-bootstrap";
import {FaArrowLeft, FaPlus} from "react-icons/fa";
import {CompletionStatus, MatchInProgress, MatchOutcomes, Participant, ParticipantVictories} from "./models";
import {fetchParticipantVictories, getMatchCompletion} from "./match_service";
import {CLASSES} from "../../models";
import ProgressCounter from "./progress_counter";

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

interface RenderedParticipantVictories extends ParticipantVictories {
    participant: Participant
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

    const RANGES = Object.keys(params.match.duels).map(Number)

    // results by class + range
    let results: {[key: string]: {[key: number]: RenderedParticipantVictories[]}} = {}
    for (const clazz of CLASSES) {
        let classResultsByRange: {[key: number]: RenderedParticipantVictories[]} = {}
        for (const rng of RANGES) {
            classResultsByRange[rng] = []
            const participantIDs = params.match.participants_by_range[rng].filter(
                (p) => {return params.match.participantsDict[p].clazz == clazz}
            )
            for (const participantID of participantIDs) {
                const victory = victories[participantID]
                const participant = params.match.participantsDict[participantID]
                classResultsByRange[rng].push(
                    {
                        dq: victory?.dq ?? false,
                        participant: participant,
                        participant_id: participantID,
                        victories: victory?.victories ?? 0,
                    }
                )
            }
        }
        results[clazz] = classResultsByRange
    }

    const victoriesRows = []
    for (const clazz of CLASSES) {
        for (const range of RANGES) {
            let classRangeVictories = results[clazz][range];
            if (classRangeVictories.length == 0) {
                continue
            }
            const status = getMatchCompletion(
                params.match, params.outcomes,
                {range: range, clazz: clazz}
            )
            victoriesRows.push(
                <RangeClassResults
                    key={ clazz + range }
                    clazz={clazz}
                    range={range}
                    victories={classRangeVictories}
                    status={status}
                />
            )
        }
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

interface RangeClassResultsParams {
    clazz: string
    range: number
    victories: RenderedParticipantVictories[]
    status: CompletionStatus
}

function RangeClassResults(params: RangeClassResultsParams) {
    params.victories.sort(
        (a, b) => {
            if (a.victories < b.victories)
                return 1
            if (a.victories > b.victories)
                return -1
            return 0
        }
    )
    const topVictoryCounts = [...(new Set(
            params.victories.map(v => v.victories)
    ))].sort((a, b) => b - a).slice(0, 4)

    const isCompleted = params.status.completed == params.status.total

    const rows = params.victories.map(
        (v) => {
            const isWinner = topVictoryCounts.includes(v.victories)
            let badge = <></>
            if (isCompleted) {
                if (v.dq) {
                    badge = <Badge bg={"danger"}>dq</Badge>
                } else if (isWinner) {
                    badge = <Badge bg={"success"}>Півфінал</Badge>
                }
            }
            return (
                <tr key={v.participant.id}>
                    <td>{v.participant.name}</td>
                    <td>{v.victories} {badge}</td>
                </tr>
            )
        }
    )
    return (
        <>
            <h2>{params.clazz} - рубіж №{params.range} <ProgressCounter status={params.status}/></h2>
            <Table>
                <thead>
                    {rows}
                </thead>
                <tbody>

                </tbody>
            </Table>
        </>
    )
}