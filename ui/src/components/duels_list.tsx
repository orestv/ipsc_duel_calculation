import React from "react";
import {Match, RANGES} from "../models";

export interface DuelsListProps {
    match: Match | null
    isLoading: boolean
}

export default function DuelsList(props: DuelsListProps) {
    if (props.isLoading) {
        return <h2>Loading...</h2>
    }
    if (!props.match) {
        return <></>
    }
    if (!props.match.ranges) {
        return <></>
    }

    const ranges = []
    for (const range of RANGES) {
        const duels = props.match.ranges[range] || []

        const rows = []
        for (const duel of duels) {
            rows.push(<tr key={duel.left.name + duel.right.name}>
                <td>{duel.left.name}</td>
                <td>{duel.right.name}</td>
                <td>{duel.clazz}</td>
            </tr>)
        }

        const tbody = <tbody>{rows}</tbody>
        const tbl = (
            <div className="col" key={range}>
                <h2>Рубіж {range} <span className="badge bg-secondary">{duels.length}</span> </h2>
                <table className="table">
                    <thead>
                    <tr>
                        <th scope="col">Зліва</th>
                        <th scope="col">Справа</th>
                        <th scope="col">Клас</th>
                    </tr>
                    </thead>
                    { tbody }
                </table>
            </div>
        )
        ranges.push(tbl)
    }
    return (
        <>
            <div className="row">
                {ranges}
            </div>
        </>
    )
}
