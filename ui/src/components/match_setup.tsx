import React, {useEffect, useState} from "react";
import {getMatchSetupFromLocalStorage} from "../legacy/legacy";
import {CLASSES, ClassSetupRequest, MatchSetupRequest, RANGES} from "../models";
import ClassSetup from "./class_setup";

export default function MatchSetup() {
    const defaultMatchSetup: MatchSetupRequest = {
        ranges: {}
    }

    const [matchSetup, setMatchSetup] = useState(defaultMatchSetup)

    const participantsChangedHandler = function(range: string, clazz: string, c: ClassSetupRequest) {
        setMatchSetup(
            {
                ...matchSetup,
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

    const ranges = []
    for (const range of RANGES) {
        const r = matchSetup.ranges[range];
        const defaultSetup: ClassSetupRequest = {participants: [], twice: false}
        const classes = r ? r.classes : {}
        const classControls = []
        for (const clazz of CLASSES) {
            const setup = classes[clazz] || defaultSetup
            classControls.push(
                <div className="col">
                    <ClassSetup
                        className={clazz}
                        classSetup={setup}
                        onParticipantsChanged={(c) => participantsChangedHandler(range, clazz, c)}/>
                </div>
            )
        }
        ranges.push(
            <>
                <div className="row">
                    <h1>Рубіж {range}</h1>
                    { classControls }
                </div>
            </>
        )
    }

    return <div className="container-fluid py-3">
        <form action="#">
            { ranges }
        </form>
    </div>
}
