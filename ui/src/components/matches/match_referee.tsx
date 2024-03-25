import React, {useEffect, useState} from "react";
import {useLoaderData} from "react-router-dom";
import {MatchInProgress, MatchOutcomes} from "./models";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Alert, Button, ButtonGroup, Col, Form, InputGroup, Row, Spinner, Stack, ToggleButton} from "react-bootstrap";
import DuelList from "./duel_list";
import {fetchMatchInProgress, fetchMatchOutcomes, getMatchCompletion, getRangeCompletion} from "./match_service";
import ProgressCounter from "./progress_counter";
import {MatchResultsModal} from "./match_results";

export async function loader({params}: any) {
    return <>
        <MatchReferee matchId={params.matchId}/>
    </>
}

export const MatchOutcomesComponent = () => useLoaderData() as React.JSX.Element


interface MatchRefereeParams {
    matchId: string
}

export function MatchReferee(params: MatchRefereeParams) {
    const defaultMatch = (): MatchInProgress => {
        return {
            created_at: undefined,
            duels: {},
            id: "",
            name: "",
            participants: [],
            participants_by_range: {},
            participantsDict: {}
        }
    }
    const [match, setMatch] = useState(defaultMatch())

    // state for fetching match outcomes, displays the match or something.
    const [outcomesStale, setOutcomesStale] = useState(false)
    const defaultOutcomes = (): MatchOutcomes => {
        return {outcomes: {}}
    }
    const [outcomes, setOutcomes] = useState(defaultOutcomes())
    useEffect(() => {
        (async () => {
            setMatch(await fetchMatchInProgress(params.matchId))
            setOutcomes(await fetchMatchOutcomes(params.matchId))
            setOutcomesStale(false)
        })()
    }, [outcomesStale]);

    const handleOutcomeRecorded = async () => {
        setOutcomesStale(true)
        // setOutcomes(await fetchMatchOutcomes(params.matchId))
    }

    const ranges = Object.keys(match.duels ?? {}).map(Number)
    const [selectedRange, setSelectedRange] = useState(1)
    const rangeButtons = []
    for (const r of ranges) {
        rangeButtons.push(
            <ToggleButton
                variant={"outline-primary"}
                type={"radio"}
                checked={selectedRange == r}
                onChange={(e) => {
                    setSelectedRange(Number(e.currentTarget.value))
                }}
                key={r}
                id={`range-${r}`} value={r}>
                Рубіж {r}
            </ToggleButton>
        )
    }

    const defaultMatchCompletion = getMatchCompletion(match, outcomes, {
        range: selectedRange
    })
    const [matchCompletionStatus, setMatchCompletionStatus] = useState(defaultMatchCompletion)
    const getNextDuel = (): number => {
        for (const duel of match.duels[selectedRange] ?? []) {
            if (!(duel.id in outcomes.outcomes)) {
                return duel.order
            }
        }
        return null
    }
    useEffect(() => {
        setNextDuel(getNextDuel())
        setMatchCompletionStatus(
            getMatchCompletion(match, outcomes, {
                range: selectedRange
            })
        )
    }, [outcomes, match]);
    const [nextDuel, setNextDuel] = useState(getNextDuel())

    const [showResults, setShowResults] = useState(false)

    return <>
        <Navbar sticky={"top"} expand={"sm"} className={"bg-body-secondary"}>
            <Container fluid className={"justify-content-between"}>
                <Navbar.Brand>Наступна дуель: <b>{nextDuel}</b></Navbar.Brand>
                <Button
                    onClick={() => {
                        setShowResults(true)
                    }}
                >
                    Результати <ProgressCounter status={matchCompletionStatus}/>
                </Button>
            </Container>
        </Navbar>
        <Container fluid>
            <Row className={"my-3"}>
                <Col>
                    <ButtonGroup className='d-flex justify-content-between'>
                        {rangeButtons}
                    </ButtonGroup>
                </Col>
            </Row>
            <Row>
                <Col>
                    <DuelList
                        matchId={params.matchId}
                        range={selectedRange}
                        duels={match.duels[selectedRange] ?? []}
                        outcomes={outcomes}
                        onOutcomeRecorded={handleOutcomeRecorded}
                    />
                </Col>
            </Row>
        </Container>
        <MatchResultsModal key={match.id} match={match} outcomes={outcomes} show={showResults} onHide={() => {
            setShowResults(false)
        }}/>
    </>
}