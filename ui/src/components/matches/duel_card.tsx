import React, {useEffect, useState} from "react";
import {DuelDQ, DuelOutcome, DuelVictory, MatchDuel} from "./models";
import {
    Accordion, AccordionItem, Alert,
    Button,
    ButtonGroup,
    Card,
    Form,
    Modal,
    Stack,
    ToggleButton,
    ToggleButtonGroup
} from "react-bootstrap";
import {recordOutcome} from "./match_service";
import {types} from "sass";
import Boolean = types.Boolean;
import Container from "react-bootstrap/Container";

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
        const outcomeDateString = outcomeDate.toLocaleTimeString('uk-UA', {hour12: false}) ?? ''
        return (
            <>
                <span>{outcomeDateString}</span>
            </>
        )
    }
    const duelActions = (outcome?: DuelOutcome) => {
        if (outcome == undefined) {
            return (
                <Button variant='primary' onClick={() => {
                    setShowModal(true)
                }}>Судити</Button>
            )
        }
        return (
            <Button variant={'outline-secondary'} onClick={() => {
                setShowModal(true)
            }}>Перезаписати</Button>
        )
    }
    const defaultShowModal = params.duel.id == "a2df0ee2-65b9-4c71-a330-797ce3ca79d6" //todo: remove debug
    const [showModal, setShowModal] = useState(defaultShowModal)
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
            <Card className={"my-5"} style={{width: '100%'}}>
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
            <OutcomeModal
                onClose={handleClose}
                show={showModal}
                leftName={participantLeft}
                rightName={participantRight}
                outcome={params.outcome}
            />
        </>
    )
}

interface OutcomeModalParams {
    leftName: string
    rightName: string
    show: boolean
    outcome?: DuelOutcome
    onClose: (victory?: DuelVictory, dq?: DuelDQ) => void
}

enum Victory {
    Left = "left",
    None = "none",
    Right = "right",
}

interface DQ {
    left: boolean
    right: boolean
}

interface Judgement {
    victory?: DuelVictory
    dq?: DuelDQ
}

function OutcomeModal(params: OutcomeModalParams) {
    const parseVictory = (outcome: DuelOutcome): Victory => {
        if (outcome == null) {
            return null
        }
        if (outcome.victory.right) {
            return Victory.Right
        }
        if (outcome.victory.left) {
            return Victory.Left
        }
        return Victory.None
    }

    const [victory, setVictory] = useState(parseVictory(params.outcome))
    const handleVictoryChanged = (val: Victory) => {
        setVictory(val)
    }

    const defaultDQ: string[] = []
    if (params.outcome?.dq?.left) {
        defaultDQ.push("left")
    }
    if (params.outcome?.dq?.right) {
        defaultDQ.push("right")
    }
    const [dq, setDQ] = useState(defaultDQ)
    const handleDQChanged = (e: string[]) => {
        setDQ(e)

        if (e.includes("left") && victory == Victory.Left) {
            setVictory(Victory.None)
        }
        if (e.includes("right") && victory == Victory.Right) {
            setVictory(Victory.None)
        }
    }

    const defaultJudgement: Judgement = {}
    const [judgement, setJudgement] = useState(defaultJudgement)

    useEffect(() => {
        let newJudgement: Judgement = {}
        if (victory) {
            newJudgement.victory = {left: false, right: false}
            if (victory == Victory.Left) {
                newJudgement.victory.left = true
            }
            if (victory == Victory.Right) {
                newJudgement.victory.right = true
            }
        }
        if (dq.length > 0) {
            newJudgement.dq = {left: dq.includes("left"), right: dq.includes("right")}
        }
        setJudgement(newJudgement)
        setCanSubmit(Object.keys(newJudgement).length > 0)
    }, [victory, dq]);
    const handleSubmit = (event: any) => {
        event.preventDefault()
        event.stopPropagation()
        params.onClose(
            judgement.victory,
            judgement.dq,
        )
    }

    const [canSubmit, setCanSubmit] = useState(false)

    const handleHide = () => {
        setVictory(parseVictory(params.outcome))
        setDQ(defaultDQ)
        params.onClose(null, null)
    }

    return (
        <Modal show={params.show} onHide={handleHide}>
            <Modal.Header closeButton>
                <Modal.Title><b>{params.leftName}</b> vs <b>{params.rightName}</b></Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <OutcomeRender outcome={params.outcome} leftName={params.leftName} rightName={params.rightName}/>
            </Modal.Body>
            <Modal.Footer className='d-flex justify-content-between'>
                <Form onSubmit={handleSubmit}>
                    <Form.Group className={"mb-3"}>
                        <ToggleButtonGroup
                            name={"victory"}
                            type={"radio"}
                            value={victory}
                            onChange={handleVictoryChanged}
                        >
                            <ToggleButton
                                id={"win-left"}
                                value={"left"}
                                variant={"outline-primary"}
                                disabled={dq.includes("left")}
                                checked={victory == Victory.Left}
                            >Перемога зліва</ToggleButton>
                            <ToggleButton
                                id={"win-none"}
                                value={"none"}
                                variant={"outline-primary"}
                                checked={victory == Victory.None}
                            >Дві поразки</ToggleButton>
                            <ToggleButton
                                id={"win-right"}
                                value={"right"}
                                variant={"outline-primary"}
                                disabled={dq.includes("right")}
                                checked={victory == Victory.Right}
                            >Перемога справа</ToggleButton>
                        </ToggleButtonGroup>
                    </Form.Group>
                    <Accordion defaultActiveKey={dq.length > 0 ? "0" : null}>
                        <AccordionItem eventKey={"0"}>
                            <Accordion.Header>DQ</Accordion.Header>
                            <Accordion.Body>
                                <Form.Group className={"mb-3"}>
                                    <ToggleButtonGroup
                                        name={"dq"}
                                        type={"checkbox"}
                                        defaultValue={dq}
                                        className='d-flex justify-content-between'
                                        onChange={handleDQChanged}
                                    >
                                        <ToggleButton
                                            id={"dq-left"}
                                            value={"left"}
                                            variant={"outline-danger"}
                                            checked={dq.includes("left")}
                                        >DQ зліва</ToggleButton>
                                        <ToggleButton
                                            id={"dq-right"}
                                            value={"right"}
                                            variant={"outline-danger"}
                                            checked={dq.includes("right")}
                                        >DQ справа</ToggleButton>
                                    </ToggleButtonGroup>
                                </Form.Group>
                            </Accordion.Body>
                        </AccordionItem>
                    </Accordion>
                    <Container className={"mt-3 d-flex justify-content-between"}>
                        <Button size={"lg"} disabled={!canSubmit} type={"submit"}>Зберегти результат</Button>
                        <Button size={"lg"} variant={"outline-dark"} onClick={handleHide}>Закрити</Button>
                    </Container>
                </Form>
                {/*{JSON.stringify(judgement)}*/}
                {/*<Button variant="primary" onClick={() => params.handleClose({left: true, right: false})}>Перемога зліва</Button>*/}
                {/*<Button variant="primary" onClick={() => params.handleClose({left: false, right: true})}>Перемога справа</Button>*/}
            </Modal.Footer>
        </Modal>
    )
}

interface OutcomeRenderParams {
    outcome?: DuelOutcome
    leftName: string
    rightName: string
}

function OutcomeRender(params: OutcomeRenderParams) {
    if (!params.outcome)
        return <>Дуель ще не відбулась</>

    let victoryText = ""
    if (params.outcome.victory.left) {
        victoryText = `Переміг зліва (${params.leftName}).`
    } else if (params.outcome.victory.right) {
        victoryText = `Переміг справа (${params.rightName}).`
    } else {
        victoryText = "Дві поразки."
    }
    let alertsDQ = []
    if (params.outcome.dq?.left) {
        alertsDQ.push(
            <Alert variant={"danger"}>DQ: {params.leftName}</Alert>
        )
    }
    if (params.outcome.dq?.right) {
        alertsDQ.push(
            <Alert variant={"danger"}>DQ: {params.rightName}</Alert>
        )
    }

    return (
        <>
            <Alert>
                <p>
                    Дуель проведено {(new Date(params.outcome.created_at)).toLocaleTimeString('uk-UA', {hour12: false})}
                </p>
                {victoryText}
            </Alert>
            {alertsDQ}
        </>
    )
}