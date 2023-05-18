import React, {useState} from "react";
import {CLASSES, EmptyMatchSetupRequest, MatchSetupRequest} from "../models";

export interface MatchLoaderProps {
  visible: boolean
  onMatchLoaded: (m: MatchSetupRequest) => void
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

function getDefaultTAValue() {
  return " 1.\n" +
    "Винар Роман\n" +
    "1\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "2.\n" +
    "Вострес Олександр\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "3.\n" +
    "Гнідець Петро\n" +
    "1\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Відкритий\n" +
    "4.\n" +
    "Корсун Павло\n" +
    "1\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "5.\n" +
    "Кукурудз Володимир\n" +
    "1\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "6.\n" +
    "Мацех Анастасия\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Стандарт\n" +
    "7.\n" +
    "Мороз Євген\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "8.\n" +
    "Павлюк Олег\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "9.\n" +
    "Перожак Ростислав\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "10.\n" +
    "Поронович Тарас\n" +
    "1\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "11.\n" +
    "Пут Ігор\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "12.\n" +
    "Рогозін Олександр\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "13.\n" +
    "Свінчук Володимир\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "14.\n" +
    "Синяк Юрій\n" +
    "1\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "15.\n" +
    "Юзвик Денис\n" +
    "1\n" +
    "Зареєстровано\n" +
    "Стандарт\n" +
    "16.\n" +
    "Koval Volodymyr\n" +
    "2\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "17.\n" +
    "Kozlovskyi Dmytro\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "18.\n" +
    "Zub Lyubomyr\n" +
    "2\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Відкритий\n" +
    "19.\n" +
    "Антін Кульба\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Відкритий\n" +
    "20.\n" +
    "Барінов Олександр\n" +
    "2\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "21.\n" +
    "Волощук Орест\n" +
    "2\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "22.\n" +
    "Дубик Роман\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "23.\n" +
    "Кардаш Іван\n" +
    "2\n" +
    "Очікує\n" +
    "Стандарт-мануал\n" +
    "24.\n" +
    "Ласкавий Антон\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "25.\n" +
    "Ремез Олександр\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "26.\n" +
    "Скіць Ірина\n" +
    "2\n" +
    "Очікує\n" +
    "Леді\n" +
    "Стандарт\n" +
    "27.\n" +
    "Скороход Вадим\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "28.\n" +
    "Хомів Василь\n" +
    "2\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "29.\n" +
    "Чхало Дмитро\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Відкритий\n" +
    "30.\n" +
    "Шкап'як Тарас\n" +
    "2\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "31.\n" +
    "Dovganyk Volodymyr\n" +
    "3\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "32.\n" +
    "Валько Сергій\n" +
    "3\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "33.\n" +
    "Горбатюк Антон\n" +
    "3\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Відкритий\n" +
    "34.\n" +
    "Дияк Гліб\n" +
    "3\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "35.\n" +
    "Когут Володимир\n" +
    "3\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "36.\n" +
    "Кравчута Сергій\n" +
    "3\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт\n" +
    "37.\n" +
    "Мисник Юра\n" +
    "3\n" +
    "Очікує\n" +
    "Загальна\n" +
    "Модифікований\n" +
    "38.\n" +
    "Подоляк Меланія-Марія\n" +
    "3\n" +
    "Очікує\n" +
    "Леді\n" +
    "Стандарт\n" +
    "39.\n" +
    "Козаченко Віктор\n" +
    "4\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт-мануал\n" +
    "40.\n" +
    "Корень Ярослав\n" +
    "4\n" +
    "Зареєстровано\n" +
    "Загальна\n" +
    "Стандарт"
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

  const rangeSetup = Object.fromEntries(classList.map(({clazz, ...rest}) => ([clazz, rest])))

  result.ranges["1"].classes = rangeSetup

  return result
  // return {
  //   "ranges": {
  //     "1": {"classes": {
  //       "SL": {
  //         "participants": ["one", "two", "three"],
  //         "twice": false,
  //       }
  //       }},
  //   }
  // }
}

export default function MatchLoader(props: MatchLoaderProps) {
  const [taValue, setTaValue] = useState(getDefaultTAValue())

  const handleTextAreaValueChanged = function (e: React.ChangeEvent<HTMLTextAreaElement>) {
    const newValue = e.target.value;
    setTaValue(newValue)
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
    </div>
  </div>
}
