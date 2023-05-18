import React, {useState} from "react";
import {CLASSES, EmptyMatchSetupRequest, MatchSetupRequest} from "../models";

export interface MatchLoaderProps {
  visible: boolean
  onMatchLoaded: (m: MatchSetupRequest) => void
  onCanceled: () => void
}

interface Participant {
  name: string
  clazz: string
}

function convertClass(classVerbose: string, category: string): string {
  const mapping: { [key: string]: string } = {
    "Стандарт": "S",
    "Стандарт-мануал": "SM",
    "Модифікований": "M",
    "Відкритий": "O"
  }
  const clazz = mapping[classVerbose]
  if (clazz == "S" && category == "Леді")
    return "SL"
  console.log(classVerbose, category)
  return clazz
}

function getParticipant(chunk: string[]): Participant {
  const name = chunk[1]
  const clazzVerbose = chunk[chunk.length-1]
  const category = chunk.length == 6 ? chunk[chunk.length-2] : "Загальна"
  const clazz = convertClass(clazzVerbose, category)
  return {name: name, clazz: clazz}
}

function getMatchSetup(taValue: string): MatchSetupRequest {
  let result = EmptyMatchSetupRequest()
  const rows = taValue.trim().split("\n")
  const re = new RegExp("[0-9]{1,2}\\.")
  let indices = rows.map((val, idx, _) => {
    if (re.test(val)) {
      return idx
    }
  }).filter((val) => {
    return val != null
  })
  indices.push(rows.length)

  let indexPairs: number[][] = []
  for (let idx = 0; idx < indices.length - 1; idx++) {
    indexPairs.push([indices[idx], indices[idx + 1]])
  }

  let chunks: string[][] = []

  for (const [first, last] of indexPairs) {
    chunks.push(rows.slice(first, last))
  }

  const participants = chunks.map(getParticipant)
  console.log(participants)

  const classList = CLASSES.map(
    (clazz) => {
      const classParticipants = participants
        .filter((p) => (p.clazz == clazz))
        .map((p) => (p.name))
      return {
        "clazz": clazz,
        "participants": classParticipants,
        "twice": false,
      }
    }
  )

  result.ranges["1"].classes = Object
    .fromEntries(
      classList.map(({clazz, ...rest}) => ([clazz, rest]))
    )

  return result
}

export default function MatchLoader(props: MatchLoaderProps) {
  const [taValue, setTaValue] = useState("")

  const handleTextAreaValueChanged = function (e: React.ChangeEvent<HTMLTextAreaElement>) {
    const newValue = e.target.value;
    setTaValue(newValue)
  }

  const handleSaveMatchClicked = () => {
    const matchSetup = getMatchSetup(taValue)
    props.onMatchLoaded(matchSetup)
  }

  if (!props.visible) {
    return <></>
  }
  return <div className="card">
    <div className="card-body">
      <h2 className="card-title">Завантаження списку з practicarms</h2>

      <label htmlFor="textareaPracticarmsList">
        Скопіюйте усю таблицю учасників з practicarms у поле вводу нижче. <br/>
        Переконайтесь, що ви скопіювали усі поля в усіх рядках (включно з номером, класом, категорією, ...). <br/>
        Копіювати заголовок таблиці не потрібно.
      </label>
      <textarea
        className="form-control" rows={20}
        id={"textareaPracticarmsList"}
        value={taValue}
        onChange={handleTextAreaValueChanged}
      />
      <button type="button" className="btn btn-primary" onClick={handleSaveMatchClicked}>⬇️Зберегти</button>
      <button type="button" className="btn btn-secondary" onClick={props.onCanceled}>Закрити</button>
    </div>
  </div>
}
