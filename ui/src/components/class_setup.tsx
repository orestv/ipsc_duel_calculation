import React, {ChangeEventHandler, Fragment, useState} from "react";
import {ClassSetupRequest} from "../models";

export interface ClassSetupProps {
    className: string
    participants: string[]
    twice: boolean
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
    const textAreaValue = props.participants.join("\n")
    const [value, setValue] = useState("");

    const changeHandler = function(e: React.ChangeEvent<HTMLTextAreaElement>) {
        setValue(e.target.value)
        let participants = e.target.value.split("\n")
        participants = participants.filter((p) => p.length > 0)
        props.onParticipantsChanged({
            participants: participants,
            twice: false,
        })
    }

    return (
        <>
            <div className="col">
                <h4>{classNames[props.className]}</h4>
                <textarea
                    rows={8}
                    className="form-control"
                    defaultValue={textAreaValue}
                    onChange={changeHandler}
                />
            </div>
        </>
    )
}
