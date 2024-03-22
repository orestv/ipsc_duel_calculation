import React, {useEffect, useState} from "react";
import {useLoaderData} from "react-router-dom";
import {MatchInProgress, MatchOutcomes, Participant} from "./models";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Button, Row} from "react-bootstrap";
import DuelList from "./duel_list";
import {fetchMatchInProgress, fetchMatchOutcomes} from "./match_service";
import ProgressCounter from "./progress_counter";

export async function loader({params}: any) {
    return <>
        <MatchReferee matchId={params.matchId}/>
    </>
}

export const MatchOutcomesComponent = () => useLoaderData() as JSX.Element


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

    const rangeDuels = match.duels[selectedRange] ?? []
    const rangeDuelIDs = rangeDuels.map((d) => {return d.id})
    const totalDuels = rangeDuels.length
    const completedDuels = Object.keys(outcomes.outcomes).filter(
        (val) => {return rangeDuelIDs.includes(val)}
    ).length

    return <>
        <h1>Матч "{match.name}" <ProgressCounter total={totalDuels} completed={completedDuels}/></h1>
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
                    outcomes={outcomes.outcomes}
                    onOutcomeRecorded={handleOutcomeRecorded}
                />
            </Row>
        </Container>
    </>
}