import React, {useEffect, useState} from "react";
import MatchSetup from "./match_setup";
import DuelsList from "./duels_list";
import {Match, MatchSetupRequest} from "../models";
import {API_ROOT} from "../storage";

export default function App() {
    const defaultMatchSetup: MatchSetupRequest = {ranges: {}}
    const [matchSetup, setMatchSetup] = useState(defaultMatchSetup)
    const [match, setMatch] = useState(null)
    const [isLoading, setLoading] = useState(false)

    const handleMatchSetup = function(r: MatchSetupRequest) {
        setMatchSetup(r)
    }

    useEffect(() => {
        (async () => {
            setLoading(true)
            const response = await fetch(
                `${API_ROOT}/duels`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    mode: "cors",
                    body: JSON.stringify(matchSetup),
                }
            );
            const receivedMatch : Match = JSON.parse(await response.text())
            setLoading(false)
            setMatch(receivedMatch)

        })()
    }, [matchSetup])

    return (
        <>
            <div className="container-fluid my-4">
                <MatchSetup onMatchSetup={handleMatchSetup}/>
            </div>
            <div className="container-fluid my-4">
                <DuelsList match={match} isLoading={isLoading}/>
            </div>
        </>
    )
}
