import React, {useEffect, useState} from "react";
import Container from "react-bootstrap/Container";
import {Button, Table} from "react-bootstrap";
import {deleteMatch, fetchMatches} from "./match_service";
import {MatchInProgress} from "./models";
import {FaDeleteLeft} from "react-icons/fa6";
import {FaTrash} from "react-icons/fa";

export default function MatchList() {
    const emptyMatches: MatchInProgress[] = []
    const [matches, setMatches] = useState(emptyMatches)

    useEffect(() => {
        (async () => {
            const matches = await fetchMatches()
            setMatches(matches)
        })()
    }, []);

    const buildMatchDeleteClickHandler = (matchId: string) => {
        return async (e: any) => {
            await deleteMatch(matchId)
            const matches = await fetchMatches()
            setMatches(matches)
        }
    }

    const rows = []
    for (const match of matches) {
        const createdAt = match.created_at != null ? match.created_at.toLocaleString() : 'N/A'
        rows.push(
            <tr key={match.id}>
                <td></td>
                <td>{match.name}</td>
                <td>{createdAt}</td>
                <td></td>
                <td>
                    <Button variant="danger" onClick={buildMatchDeleteClickHandler(match.id)}><FaTrash/></Button>
                </td>
            </tr>
        )
    }

    return (
        <>
            <h1>Match list be here!</h1>
            <Container>
                <Table>
                    <thead>
                    <tr>
                        <th>#</th>
                        <th>Назва</th>
                        <th>Дата</th>
                        <th>Статус</th>
                        <th>Дії</th>
                    </tr>
                    </thead>
                    <tbody>
                    {rows}
                    </tbody>
                </Table>
            </Container>
        </>
    )
}