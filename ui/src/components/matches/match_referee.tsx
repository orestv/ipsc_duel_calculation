import React, {useEffect, useState} from "react";
import {useLoaderData} from "react-router-dom";
import {MatchInProgress, MatchOutcomes} from "./models";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Button, ButtonGroup, Row, Stack, ToggleButton} from "react-bootstrap";
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
    useEffect(() => {
        (async () => {
            setMatch(await fetchMatchInProgress(params.matchId))
        })()
    }, []);

    const [outcomesUpdated, setOutcomesUpdated] = useState(true)
    const defaultOutcomes = (): MatchOutcomes => {
        return {outcomes: {}}
    }
    const [outcomes, setOutcomes] = useState(defaultOutcomes())

    useEffect(() => {
        (async () => {
            setOutcomes(await fetchMatchOutcomes(params.matchId))
            setOutcomesUpdated(true)
        })()
    }, [outcomesUpdated]);

    const handleOutcomeRecorded = async () => {
        setOutcomes(await fetchMatchOutcomes(params.matchId))
    }

    const ranges = Object.keys(match.duels).map(Number)
    const [selectedRange, setSelectedRange] = useState(1)
    const rangeButtons = []
    for (const r of ranges) {
        rangeButtons.push(
            <ToggleButton
                variant={"outline-primary"}
                type={"radio"}
                checked={selectedRange == r}
                onChange={(e) => {setSelectedRange(Number(e.currentTarget.value))}}
                key={r}
                id={`range-${r}`} value={r}>
                Рубіж {r}
            </ToggleButton>
        )
    }

    const matchCompletionStatus = getMatchCompletion(
        match, outcomes, {
            range: selectedRange
        }
    )

    const [showResults, setShowResults] = useState(false)

    return <>
        <h1>
            <Stack direction={"horizontal"} gap={1}>
                Матч "{match.name}"
                <ProgressCounter status={matchCompletionStatus}/>
                <ButtonGroup>
                    {rangeButtons}
                </ButtonGroup>
            </Stack>
        </h1>
        <Navbar>
            <Container>
                {/*<Link to={`/matches/${params.matchId}/results`}>*/}
                <Button onClick={() => {
                    setShowResults(true)
                }}>Результати</Button>
                {/*</Link>*/}
            </Container>
            <Container>

            </Container>
        </Navbar>
        <Container fluid>
            <Row>
                <DuelList
                    matchId={params.matchId}
                    range={selectedRange}
                    duels={match.duels[selectedRange] ?? []}
                    outcomes={outcomes}
                    onOutcomeRecorded={handleOutcomeRecorded}
                />
            </Row>
        </Container>
        <MatchResultsModal key={match.id} match={match} outcomes={outcomes} show={showResults} onHide={() => {
            setShowResults(false)
        }}/>
    </>
}