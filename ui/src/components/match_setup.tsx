import React from "react";
import {CLASSES, ClassSetupRequest, MatchSetupRequest, RANGES} from "../models";
import ClassSetup from "./class_setup";

export interface MatchSetupProps {
  matchSetup: MatchSetupRequest
  onMatchSetup: (r: MatchSetupRequest) => void
}

export default function MatchSetup(props: MatchSetupProps) {
  const participantsChangedHandler = function (range: string, clazz: string, c: ClassSetupRequest) {
    const newMatchSetup = {
      ranges: {
        ...props.matchSetup.ranges,
        [range]: {
          classes: {
            ...props.matchSetup.ranges[range].classes,
            [clazz]: c
          }
        }
      }
    }
    console.log("Participant list changed:")
    console.log(newMatchSetup)
    props.onMatchSetup(newMatchSetup)
  }

  const ranges = []
  for (const range of RANGES) {
    const r = props.matchSetup.ranges[range];
    const defaultSetup: ClassSetupRequest = {participants: [], twice: false}
    const classes = r ? r.classes : {}
    const classControls = []
    for (const clazz of CLASSES) {
      const setup = classes[clazz] || defaultSetup
      classControls.push(
        <div className="col" key={`${range}-${clazz}`}>
          <ClassSetup
            className={clazz}
            classSetup={setup}
            onParticipantsChanged={(c) => participantsChangedHandler(range, clazz, c)}/>
        </div>
      )
    }
    ranges.push(
      <div className="row py-3" key={range}>
        <h1>Рубіж {range}</h1>
        {classControls}
      </div>
    )
  }

  return (
    <>
      {ranges}
    </>
  )
}
