import React, {ChangeEventHandler, Fragment, useState} from "react";
import {ClassSetupRequest} from "../models";

export interface ClassSetupProps {
    className: string
    classSetup: ClassSetupRequest
    onParticipantsChanged: (p: ClassSetupRequest) => void
}

const classNames: { [key: string]: string } = {
    "S": "Стандарт",
    "SL": "Стандарт Леді",
    "SM": "Стандарт-мануал",
    "M": "Модифікований",
    "O": "Відкритий",
}

export default function ClassSetup(props: ClassSetupProps) {
    const textAreaValue = props.classSetup.participants.join("\n")

    const parseParticipants = function(val: string) : string[] {
        return val.split("\n")//.filter((p) => p.length > 0)
    }

    const taChangeHandler = function(e: React.ChangeEvent<HTMLTextAreaElement>) {
        const participants = parseParticipants(e.target.value)
        props.onParticipantsChanged({
            ...props.classSetup,
            participants: participants,
        })
    }
    const twiceChangeHandler = function(e: React.ChangeEvent<HTMLInputElement>) {
        const newChecked = e.target.checked
        props.onParticipantsChanged({
            ...props.classSetup,
            twice: newChecked
        })
    }

    const nonEmptyParticipants = props.classSetup.participants.filter((p) => p.length > 0)

    return (
        <>
            <div className="col">
                <h2>
                    {classNames[props.className]}
                    <span className="badge badge-primary bg-primary mx-2">{nonEmptyParticipants.length}</span>
                </h2>

                <div className="form-check form-switch">
                    <input type="checkbox"
                           role="switch"
                           className="form-check-input"
                           id="switchTwice"
                           checked={props.classSetup.twice}
                           onChange={twiceChangeHandler}
                    />
                    <label htmlFor="switchTwice" className="form-check-label">Двічі</label>
                </div>

                <textarea
                    rows={8}
                    className="form-control"
                    value={textAreaValue}
                    onChange={taChangeHandler}
                />
            </div>
        </>
    )
}
