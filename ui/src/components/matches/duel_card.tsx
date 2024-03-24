import React, {useEffect, useState} from "react";
import {DuelDQ, DuelOutcome, DuelVictory, MatchDuel} from "./models";
import {
    Accordion, AccordionItem, Alert,
    Button,
    ButtonGroup,
    Card, Col,
    Form, InputGroup,
    Modal, Row,
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
    const defaultShowModal = false
    const [showModal, setShowModal] = useState(defaultShowModal)
    const handleClose = async (victory?: DuelVictory, dq?: DuelDQ, reshoot?: boolean) => {
        if (victory != null || dq != null || reshoot) {
            const outcome: DuelOutcome = {
                duel_id: params.duel.id,
                victory: victory,
                dq: dq,
                reshoot: reshoot,
                dummy: reshoot,
            }
            await recordOutcome(params.matchId, outcome)
            params.onOutcomeRecorded()
        }
        setShowModal(false)
    }

    return (
        <>
            <Card className={"my-3"}>
                <Card.Header className='d-flex justify-content-between'>
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
    onClose: (victory?: DuelVictory, dq?: DuelDQ, reshoot?: boolean) => void
}

enum Victory {
    Left = "left",
    None = "none",
    Right = "right",
}

interface Judgement {
    victory?: DuelVictory
    dq?: DuelDQ
    reshoot?: boolean
}

function OutcomeModal(params: OutcomeModalParams) {
    const parseVictory = (outcome: DuelOutcome): Victory => {
        if (outcome?.victory == null) {
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
    }

    const [reshoot, setReshoot] = useState(false)

    const defaultJudgement: Judgement = {}
    const [judgement, setJudgement] = useState(defaultJudgement)

    useEffect(() => {
        setVictory(null)
        setDQ([])
    }, [reshoot]);

    useEffect(() => {
        if (dq.includes("left") && victory == Victory.Left) {
            setVictory(Victory.None)
        }
        if (dq.includes("right") && victory == Victory.Right) {
            setVictory(Victory.None)
        }
    }, [dq]);

    useEffect(() => {
        let newJudgement: Judgement = {}

        if (reshoot) {
            newJudgement.reshoot = true
        } else if (dq.length > 0) {
            newJudgement.dq = {left: dq.includes("left"), right: dq.includes("right")}
        } else if (victory) {
            newJudgement.victory = {left: false, right: false}
            if (victory == Victory.Left) {
                newJudgement.victory.left = true
            }
            if (victory == Victory.Right) {
                newJudgement.victory.right = true
            }
        }
        setJudgement(newJudgement)
        setCanSubmit(newJudgement.victory != null || newJudgement.reshoot)
    }, [victory, dq, reshoot]);
    const handleSubmit = (event: any) => {
        event.preventDefault()
        event.stopPropagation()
        params.onClose(
            judgement.victory,
            judgement.dq,
            judgement.reshoot
        )
    }

    const [canSubmit, setCanSubmit] = useState(false)

    const handleHide = () => {
        setReshoot(false)
        setDQ(defaultDQ)
        setVictory(parseVictory(params.outcome))
        params.onClose()
    }

    const defaultAccordionKey = (() => {
        if (dq.length > 0)
            return "dq"
        if (reshoot)
            return "reshoot"
        return null
    })()

    return (
        <Modal show={params.show} onHide={handleHide}>
            <Modal.Header closeButton>
                <Modal.Title><b>{params.leftName}</b> vs <b>{params.rightName}</b></Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <OutcomeRender outcome={params.outcome} leftName={params.leftName} rightName={params.rightName}/>
            </Modal.Body>
            <Modal.Footer className={"d-flex justify-content-between"}>
                <Form onSubmit={handleSubmit}>
                    <Form.Group className={"mb-3"}>
                        <ToggleButtonGroup
                            name={"victory"}
                            type={"radio"}
                            value={victory}
                            size={"lg"}
                            onChange={handleVictoryChanged}
                        >
                            <ToggleButton
                                id={"win-left"}
                                value={"left"}
                                variant={"outline-success"}
                                disabled={dq.includes("left") || reshoot}
                                checked={victory == Victory.Left}
                            >Перемога зліва</ToggleButton>
                            <ToggleButton
                                id={"win-none"}
                                value={"none"}
                                variant={"outline-danger"}
                                disabled={reshoot}
                                checked={victory == Victory.None}
                            >Дві поразки</ToggleButton>
                            <ToggleButton
                                id={"win-right"}
                                value={"right"}
                                variant={"outline-success"}
                                disabled={dq.includes("right") || reshoot}
                                checked={victory == Victory.Right}
                            >Перемога справа</ToggleButton>
                        </ToggleButtonGroup>
                    </Form.Group>
                    <Accordion
                        defaultActiveKey={defaultAccordionKey}
                        className={"mt-5"}
                    >
                        <AccordionItem eventKey={"dq"}>
                            <Accordion.Header>DQ</Accordion.Header>
                            <Accordion.Body>
                                <Form.Group className={"mb-3"}>
                                    <ToggleButtonGroup
                                        name={"dq"}
                                        type={"checkbox"}
                                        defaultValue={dq}
                                        size={"lg"}
                                        className='d-flex justify-content-between'
                                        onChange={handleDQChanged}
                                    >
                                        <ToggleButton
                                            id={"dq-left"}
                                            value={"left"}
                                            variant={"outline-danger"}
                                            disabled={reshoot}
                                            checked={dq.includes("left")}
                                        >DQ зліва</ToggleButton>
                                        <ToggleButton
                                            id={"dq-right"}
                                            value={"right"}
                                            variant={"outline-danger"}
                                            disabled={reshoot}
                                            checked={dq.includes("right")}
                                        >DQ справа</ToggleButton>
                                    </ToggleButtonGroup>
                                </Form.Group>
                            </Accordion.Body>
                        </AccordionItem>
                        <AccordionItem eventKey={"reshoot"}>
                            <Accordion.Header>Перестріл</Accordion.Header>
                            <Accordion.Body>
                                <ToggleButton
                                    id={`reshoot-${params.outcome?.duel_id}`}
                                    value={"reshoot"}
                                    type={"checkbox"}
                                    variant={"outline-info"}
                                    className={"d-block w-100"}
                                    checked={reshoot}
                                    onChange={
                                        (e) => {
                                            setReshoot(e.currentTarget.checked)
                                        }
                                    }
                                >
                                    Перестріл
                                </ToggleButton>
                            </Accordion.Body>
                        </AccordionItem>
                    </Accordion>
                    <Container className={"mt-5 d-flex justify-content-between"}>
                        <Button size={"lg"} variant={"outline-dark"} onClick={handleHide}>Закрити</Button>
                        <Button size={"lg"} disabled={!canSubmit} type={"submit"}>Зберегти результат</Button>
                    </Container>
                </Form>
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
    if (params.outcome.victory) {
        if (params.outcome.victory.left) {
            victoryText = `Переміг зліва (${params.leftName}).`
        } else if (params.outcome.victory.right) {
            victoryText = `Переміг справа (${params.rightName}).`
        } else {
            victoryText = "Дві поразки."
        }
    } else if(params.outcome.reshoot) {
        victoryText = "Перестріл."
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