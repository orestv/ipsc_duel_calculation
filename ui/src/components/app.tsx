import React, {useEffect, useState} from "react";
import MatchLoader from "./loader";
import MatchSetup from "./match_setup";
import DuelsList from "./duels_list";
import {EmptyMatchSetupRequest, Match, MatchSetupRequest, RangeSetupRequest} from "../models";
import {API_ROOT, getMatchSetupFromLocalStorage, saveMatchSetupToLocalStorage} from "../storage";
import Navbar from "react-bootstrap/Navbar";
import {Button, Col, Row, Stack} from "react-bootstrap";
import Container from "react-bootstrap/Container";
import {FaDownload, FaPlus, FaTrash} from "react-icons/fa";
import MatchCreateModal, {MatchCreateResult} from "./match_create_modal";
import {useNavigate} from "react-router-dom";

export default function App() {
    const [matchSetup, setMatchSetup] = useState(EmptyMatchSetupRequest())
    const [match, setMatch] = useState(null)
    const [isLoading, setLoading] = useState(false)
    const [isMatchLoaderVisible, setMatchLoaderVisible] = useState(false)

    const handleMatchSetup = function (r: MatchSetupRequest) {
        setMatchSetup(r)
    }

    const handleResetMatchClick = function () {
        if (!confirm("Це скине поточне налаштування матчу: впевнені?")) {
            return;
        }
        setMatchSetup(EmptyMatchSetupRequest())
    }

    const handleMatchLoaded = function (r: MatchSetupRequest) {
        setMatchSetup(r)
        setMatchLoaderVisible(false)
    }

    const handleMatchLoaderCanceled = () => {
        setMatchLoaderVisible(false)
    }

    useEffect(
        () => {
            const storedMatchSetup = getMatchSetupFromLocalStorage();
            setMatchSetup(storedMatchSetup);
        },
        []
    )

    useEffect(() => {
        (async () => {
            setLoading(true)
            const response = await fetch(
                `${API_ROOT}/duels`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(matchSetup),
                }
            );
            const receivedMatch: Match = JSON.parse(await response.text())
            setLoading(false)
            setMatch(receivedMatch)

        })()
        saveMatchSetupToLocalStorage(matchSetup);
    }, [matchSetup])

    async function handleExcelDownloadClicked() {
        const response = await fetch(
            `${API_ROOT}/duels/excel`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(matchSetup),
            }
        )
        const responseBody = await response.blob()
        const url = URL.createObjectURL(new Blob([responseBody]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'duels.xlsx')
        document.body.appendChild(link)
        link.click()
        link.parentNode.removeChild(link)
    }

    async function handleCreateMatchClicked() {
        setShowMatchCreateModal(true)
    }

    const [showMatchCreateModal, setShowMatchCreateModal] = useState(false)

    const navigate = useNavigate()
    const handleMatchCreateHide = async (submitted: boolean, result?: MatchCreateResult) => {
        setShowMatchCreateModal(false)
        if (!submitted || result == null) {
            return
        }
        const requestBody = {
            "name": result.name,
            "duels": match,
        }
        const response = await fetch(
            `${API_ROOT}/matches`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestBody),
            }
        )
        if (response.status != 201) {
            console.log(response.text())
            return
        }
        const matchId = JSON.parse(await response.text()) as string
        navigate(`/matches/${matchId}`)
    }

    return (
        <Stack gap={2}>
            <h1>Планування</h1>
            <Container fluid className={"d-flex justify-content-between"}>
                <Button variant={"primary"}
                        onClick={() => {
                            setMatchLoaderVisible(true)
                        }}>
                    <FaPlus/>
                    Додати список з Practicarms
                </Button>
                <Button
                    variant={"outline-danger"}
                    onClick={handleResetMatchClick}
                >
                    <FaTrash/>
                    Очистити
                </Button>
            </Container>
            <MatchLoader
                visible={isMatchLoaderVisible} onMatchLoaded={handleMatchLoaded}
                onCanceled={handleMatchLoaderCanceled}/>
            <MatchSetup onMatchSetup={handleMatchSetup} matchSetup={matchSetup}/>
            <Container className="my-4">
                <h1>Дуелі</h1>
                <Stack direction={"horizontal"} gap={3}>
                    <Button variant={"primary"} onClick={handleExcelDownloadClicked}>
                        <FaDownload/> Скачати відомість
                    </Button>
                    <Button variant={"primary"} onClick={handleCreateMatchClicked}>
                        <FaPlus/> Створити матч
                    </Button>
                </Stack>
                <Container className={"my-4"}>
                    <DuelsList match={match} isLoading={isLoading}/>
                </Container>
            </Container>
            <MatchCreateModal
                show={showMatchCreateModal}
                onHide={handleMatchCreateHide}
            />
        </Stack>
    )
}
