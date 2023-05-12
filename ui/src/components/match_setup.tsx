import React, {useEffect, useState} from "react";
import {CLASSES, ClassSetupRequest, MatchSetupRequest, RANGES} from "../models";
import ClassSetup from "./class_setup";
import {API_ROOT, getMatchSetupFromLocalStorage, saveMatchSetupToLocalStorage} from "../storage";

export interface MatchSetupProps {
    onMatchSetup: (r: MatchSetupRequest) => void
}

export default function MatchSetup(props: MatchSetupProps) {
    const defaultMatchSetup: MatchSetupRequest = {
        ranges: {
            "1": {classes: {}},
            "2": {classes: {}},
        }
    }

    const [matchSetup, setMatchSetup] = useState(defaultMatchSetup)

    const participantsChangedHandler = function(range: string, clazz: string, c: ClassSetupRequest) {
        setMatchSetup(
            {
                ranges: {
                    ...matchSetup.ranges,
                    [range]: {
                        classes: {
                            ...matchSetup.ranges[range].classes,
                            [clazz]: c
                        }
                    }
                }
            }
        )
    }

    useEffect(
        () => {
            const storedMatchSetup = getMatchSetupFromLocalStorage();
            setMatchSetup(storedMatchSetup);
        },
        []
    )
    useEffect(
        () => {
            saveMatchSetupToLocalStorage(matchSetup)
            props.onMatchSetup(matchSetup)
            const dataFetch = async () => {
                const requestOptions = {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(matchSetup),
                }
                const data = await (
                    await fetch(`${API_ROOT}/duels`, requestOptions)
                ).json()
            }
            dataFetch()
        },
        [matchSetup]
    )

    const ranges = []
    for (const range of RANGES) {
        const r = matchSetup.ranges[range];
        const defaultSetup: ClassSetupRequest = {participants: [], twice: false}
        const classes = r ? r.classes : {}
        const classControls = []
        for (const clazz of CLASSES) {
            const setup = classes[clazz] || defaultSetup
            classControls.push(
                <div className="col" key={`${range}-${clazz}`}>
                    <ClassSetup
                        className={clazz}
                        classSetup={setup}
                        onParticipantsChanged={(c) => participantsChangedHandler(range, clazz, c)}/>
                </div>
            )
        }
        ranges.push(
            <div className="row py-3" key={range}>
                <h1>Рубіж {range}</h1>
                { classControls }
            </div>
        )
    }

    return (
        <>
            { ranges }
        </>
    )
}
