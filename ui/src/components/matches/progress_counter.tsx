import React from "react";
import {CompletionStatus} from "./models";
import {Badge, ProgressBar, Spinner} from "react-bootstrap";

export interface ProgressCounterProps {
    status?: CompletionStatus
}

export default function ProgressCounter(props: ProgressCounterProps) {
    if (props.status == null)
        return <Spinner/>
    return <Badge bg={"secondary"}>{props.status.completed}/{props.status.total}</Badge>

}