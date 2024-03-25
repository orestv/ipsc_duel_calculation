import React, {useEffect, useState} from "react";
import Container from "react-bootstrap/Container";
import {Button, Modal, Stack, Table} from "react-bootstrap";
import {deleteMatch, fetchMatches, fetchMatchOutcomes, getMatchCompletion} from "./match_service";
import {FaPlay, FaTrash} from "react-icons/fa";
import {Link} from "react-router-dom";
import {CompletionStatus, MatchInProgress} from "./models";
import ProgressCounter from "./progress_counter";

export default function MatchList() {
    const emptyMatches: MatchInProgress[] = []
    const [matches, setMatches] = useState(emptyMatches)

    useEffect(() => {
        (async () => {
            const matches = await fetchMatches()
            setMatches(matches)
        })()
    }, []);

    const emptyStatuses: {[key: string]: CompletionStatus} = {}
    const [statuses, setStatuses] = useState(emptyStatuses)
    useEffect(() => {
        (async () => {
            for (const match of matches) {
                const fetchedOutcomes = await fetchMatchOutcomes(match.id)
                statuses[match.id] = getMatchCompletion(match, fetchedOutcomes)
                setStatuses({...statuses})
            }
        })()
    }, [matches]);

    const defaultDeleteMatchModalProps: DeleteMatchModalProps = {
        show: false,
        onClose: null,
        match: null,
    }
    const [deleteMatchModalProps, setDeleteMatchModalprops] = useState(defaultDeleteMatchModalProps)

    const handleMatchDeleteClose = async (matchId: string, deleteConfirmed: boolean) => {
        if (deleteConfirmed) {
            await deleteMatch(matchId)
            const matches = await fetchMatches()
            setMatches(matches)
        }

        setDeleteMatchModalprops(
            {...deleteMatchModalProps, show: false}
        )
    }

    const buildMatchDeleteClickHandler = (matchId: string) => {
        return (e: any) => {
            const match = matches.filter(
                m => m.id == matchId
            )[0]
            setDeleteMatchModalprops(
                {...deleteMatchModalProps, match: match, show: true}
            )
        }
    }

    const rows = []
    for (const match of matches) {
        const createdAt = match.created_at != null ? match.created_at.toLocaleString("uk-UA", {hour12: false}) : 'N/A'
        rows.push(
            <tr key={match.id}>
                <td>
                    <Stack>
                        <h2>{match.name} <ProgressCounter status={statuses[match.id]}/></h2>
                        <span>{createdAt}</span>
                    </Stack>
                </td>
                <td>
                    <Stack direction={"horizontal"} gap={5}>
                        <Link to={`/matches/${match.id}`}>
                            <Button size={"lg"}><FaPlay/> Судити</Button>
                        </Link>
                        <Button
                            variant="outline-danger"
                            size={"sm"}
                            onClick={buildMatchDeleteClickHandler(match.id)}
                        >
                            <FaTrash/>
                            Видалити
                        </Button>
                    </Stack>
                </td>
            </tr>
        )
    }

    return (
        <>
            <h1>Матчі</h1>
            <Container>
                <Table striped>
                    <thead>
                    <tr>
                        <th>Назва</th>
                        <th>Дії</th>
                    </tr>
                    </thead>
                    <tbody>
                    {rows}
                    </tbody>
                </Table>
            </Container>
            <DeleteMatchModal
                match={deleteMatchModalProps.match}
                show={deleteMatchModalProps.show}
                onClose={handleMatchDeleteClose}
            />
        </>
    )
}

interface DeleteMatchModalProps {
    match: MatchInProgress
    show: boolean
    onClose: (matchId: string, deleteConfirmed: boolean) => void
}

function DeleteMatchModal(props: DeleteMatchModalProps) {
    if (props.match == null) {
        return <></>
    }
    return (
        <Modal show={props.show} onHide={() => props.onClose(props.match.id, false)}>
            <Modal.Header closeButton>
                <Modal.Title>Архівувати матч {props.match.name}?</Modal.Title>
            </Modal.Header>
            <Modal.Footer>
                <Container className={"d-flex justify-content-between"}>
                    <Button
                        onClick={event => props.onClose(props.match.id, false)}
                        variant={"outline-dark"}>
                        <FaTrash/> Закрити
                    </Button>

                    <Button
                        onClick={event => props.onClose(props.match.id, true)}
                        variant={"danger"}>
                        <FaTrash/> Архівувати
                    </Button>

                </Container>
            </Modal.Footer>
        </Modal>
    )
}