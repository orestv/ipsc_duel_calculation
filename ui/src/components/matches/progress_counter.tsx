import React from "react";

export interface ProgressCounterProps {
    total: number
    completed: number
}

export default function ProgressCounter(props: ProgressCounterProps) {
    return <>Проведено: {props.completed}/{props.total}</>
}