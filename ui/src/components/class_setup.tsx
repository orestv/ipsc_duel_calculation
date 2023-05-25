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
    const timesChangeHandler = function(e: React.ChangeEvent<HTMLInputElement>) {
        const newTimes = e.target.valueAsNumber
        props.onParticipantsChanged({
            ...props.classSetup,
            times: newTimes
            // twice: newChecked
        })
    }

    const nonEmptyParticipants = props.classSetup.participants.filter((p) => p.length > 0)

    return (
        <>
            <div className="col">
                <h2>
                    {classNames[props.className]}
                    <span className="badge badge-primary bg-secondary mx-2">{nonEmptyParticipants.length}</span>
                </h2>
                <label htmlFor="inputTimes">Кількість повторень</label>
                <input
                  id={"inputTimes"}
                  type="number"
                  className={"form-control my-2"}
                  min={1}
                  max={4}
                  value={props.classSetup.times}
                  onChange={timesChangeHandler}
                />

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
