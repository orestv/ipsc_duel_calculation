import React from "react";
import ClassSetup, {ClassSetupProps} from "./class_setup";
import {CLASSES, ClassSetupRequest} from "../models";

export interface RangeSetupProps {
    number: string
    classes: { [key: string] : ClassSetupRequest }
    onParticipantsChanged: (clazz: string, c: ClassSetupRequest) => void
}

export default function RangeSetup(props: RangeSetupProps) {
    const classSetups = [];

    for (const clazz of CLASSES) {
        const participants = props.classes[clazz] ? props.classes[clazz].participants : []
        classSetups.push(
            <ClassSetup
                key={clazz}
                className={clazz}
                participants={participants}
                twice={false}
                onParticipantsChanged={(p) => {props.onParticipantsChanged(clazz, p)}}
            />
        )
    }

    return (<div className="row">
        <h1>Рубіж { props.number }</h1>
        { classSetups }
    </div>)
}
