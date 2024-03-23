import React, {useState} from "react";
import {DuelDQ, DuelOutcome, DuelVictory, MatchDuel} from "./models";
import {Button, Card, Modal} from "react-bootstrap";
import {recordOutcome} from "./match_service";

export interface DuelCardParams {
    matchId: string,
    duel: MatchDuel
    outcome?: DuelOutcome
    onOutcomeRecorded: () => void
}

interface VictoryState {
    left: ParticipantVictoryState
    right: ParticipantVictoryState
}

enum ParticipantVictoryState {
    NoRecord,
    Win,
    Loss,
    DQ,
}

function getVictoryState(outcome: boolean, win: boolean, dq: boolean): ParticipantVictoryState {
    if (!outcome) {
        return ParticipantVictoryState.NoRecord
    }
    if (dq) {
        return ParticipantVictoryState.DQ
    }
    if (win) {
        return ParticipantVictoryState.Win
    } else {
        return ParticipantVictoryState.Loss
    }
}

export default function DuelCard(params: DuelCardParams) {
    const participantLeft = params.duel.leftName
    const participantRight = params.duel.rightName
    const victoryState: VictoryState = {
        left: getVictoryState(params.outcome != undefined, params.outcome?.victory?.left, params.outcome?.dq?.left),
        right: getVictoryState(params.outcome != undefined, params.outcome?.victory?.right, params.outcome?.dq?.right),
    }
    const participantSpan = (name: string, vic: ParticipantVictoryState) => {
        const color = (() => {
            switch (vic) {
                case ParticipantVictoryState.DQ:
                    return 'text-muted'
                case ParticipantVictoryState.Win:
                    return 'text-success'
                case ParticipantVictoryState.Loss:
                    return 'text-danger'
                case ParticipantVictoryState.NoRecord:
                    return ''
            }
        })()
        return <h3 className={color}>{name}</h3>
    }
    const duelOutcome = (outcome?: DuelOutcome) => {
        if (outcome == undefined) {
            return <></>
        }
        const outcomeDate = new Date(outcome.created_at)
        return (
            <>
                <span>{outcomeDate.toLocaleTimeString('uk-UA', {hour12: false}) ?? ''}</span>
            </>
        )
    }
    const duelActions = (outcome?: DuelOutcome) => {
        if (outcome == undefined) {
            return (
                <Button variant='outline-primary' onClick={() => {
                    setShowModal(true)
                }}>Судити</Button>
            )
        }
        return (
            <Button variant={'secondary'} onClick={()=>{setShowModal(true)}}>Перезаписати</Button>
        )
    }
    const [showModal, setShowModal] = useState(false)
    const handleClose = async (victory?: DuelVictory, dq?: DuelDQ) => {
        if (victory != null || dq != null) {
            const outcome: DuelOutcome = {
                duel_id: params.duel.id,
                victory: victory,
                dq: dq,
            }
            await recordOutcome(params.matchId, outcome)
            params.onOutcomeRecorded()
        }
        setShowModal(false)
    }

    return (
        <>
            <Card className={"my-3"} style={{width: '100%'}}>
                <Card.Header className="d-flex justify-content-between">
                    {participantSpan(participantLeft, victoryState.left)}
                    {participantSpan(participantRight, victoryState.right)}
                </Card.Header>
                <Card.Body className='d-flex justify-content-between'>
                    <Card.Title>{params.duel.order}</Card.Title>
                    <Card.Subtitle>{duelOutcome(params.outcome)}</Card.Subtitle>
                    {duelActions(params.outcome)}
                </Card.Body>
            </Card>
            <OutcomeModal handleClose={handleClose} show={showModal} leftName={participantLeft} rightName={participantRight}/>
        </>
    )
}

interface OutcomeModalParams {
    leftName: string
    rightName: string
    show: boolean
    handleClose: (victory?: DuelVictory, dq?: DuelDQ) => void
}

function OutcomeModal(params: OutcomeModalParams) {
    return (
        <Modal show={params.show} onHide={() => params.handleClose(null, null)}>
            <Modal.Header closeButton>
                <Modal.Title>{params.leftName} vs {params.rightName}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {/*TODO: information about previous outcome if available*/}
                <p>Text</p>
            </Modal.Body>
            <Modal.Footer className='d-flex justify-content-between'>
                <Button variant="primary" onClick={() => params.handleClose({left: true, right: false})}>Перемога зліва</Button>
                <Button variant="primary" onClick={() => params.handleClose({left: false, right: true})}>Перемога справа</Button>
            </Modal.Footer>
        </Modal>
    )
}