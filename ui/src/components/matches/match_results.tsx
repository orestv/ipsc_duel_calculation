import React from "react";

import {Link, useLoaderData} from "react-router-dom";
import Navbar from "react-bootstrap/Navbar";
import Container from "react-bootstrap/Container";
import {Button} from "react-bootstrap";
import {FaArrowLeft} from "react-icons/fa";

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