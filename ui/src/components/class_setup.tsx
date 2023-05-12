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
    const [value, setValue] = useState(textAreaValue);

    const participants = value.split("\n").filter((p) => p.length > 0)

    const changeHandler = function(e: React.ChangeEvent<HTMLTextAreaElement>) {
        setValue(e.target.value)
        props.onParticipantsChanged({
            participants: participants,
            twice: false,
        })
    }

    return (
        <>
            <div className="col">
                <h2>
                    {classNames[props.className]}
                    <span className="badge bg-secondary">{participants.length}</span>
                </h2>

                <textarea
                    rows={8}
                    className="form-control"
                    value={value}
                    onChange={changeHandler}
                />
            </div>
        </>
    )
}
