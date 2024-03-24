import React from "react";
import {CompletionStatus} from "./models";
import {Badge, ProgressBar, Spinner} from "react-bootstrap";

export interface ProgressCounterProps {
    status?: CompletionStatus
}

export default function ProgressCounter(props: ProgressCounterProps) {
    if (props.status == null)
        return <Spinner/>
    const isCompleted = props.status.completed == props.status.total
    const bg = isCompleted ? 'success' : 'secondary'
    return <Badge bg={bg}>{props.status.completed}/{props.status.total}</Badge>

}