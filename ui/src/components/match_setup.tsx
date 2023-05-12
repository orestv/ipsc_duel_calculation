import React, {useEffect, useState} from "react";
import RangeSetup from "./range_setup";
import {getMatchSetupFromLocalStorage} from "../legacy/legacy";
import {ClassSetupRequest, MatchSetupRequest, RANGES} from "../models";

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
        const classes = r ? r.classes : {}
        ranges.push(
            <RangeSetup
                key={range}
                number={range}
                classes={classes}
                onParticipantsChanged={
                    (clazz, c) => participantsChangedHandler(range, clazz, c)
                }
            />
        )
    }

    return <div className="container-fluid py-3">
        <form action="#">
            { ranges }
        </form>
    </div>
}
