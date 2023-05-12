import React, {useState} from "react";
import ClassSetup, {ClassSetupProps} from "./class_setup";
import {CLASSES, ClassSetupRequest} from "../models";

export interface RangeSetupProps {
    number: string
    classes: { [key: string] : ClassSetupRequest }
    onParticipantsChanged: (clazz: string, c: ClassSetupRequest) => void
}

export default function RangeSetup(props: RangeSetupProps) {
    const classSetups = [];

    const defaultClassSetup : ClassSetupRequest = {
        participants: [],
        twice: false,
    }

    for (const clazz of CLASSES) {
        const classSetup = props.classes[clazz] || defaultClassSetup
        classSetups.push(
            <ClassSetup
                key={clazz}
                className={clazz}
                classSetup={classSetup}
                onParticipantsChanged={(p) => {props.onParticipantsChanged(clazz, p)}}
            />
        )
    }

    return (<div className="row">
        <h1>Рубіж { props.number }</h1>
        { classSetups }
    </div>)
}
