from __future__ import annotations

import itertools
import typing

import openpyxl
import pandas as pd
import xlsxwriter
import xlsxwriter.worksheet

from duels.model import Participant, Class, Range, Duel


def deliver_excel(duels: dict[Range, list[Duel]], path: str):
    writer = pd.ExcelWriter(path)
    range_participants = _get_participants_per_range(duels)
    all_participants = itertools.chain(*range_participants.values())

    _deliver_participants(all_participants, writer)
    ranges = list(sorted(Range.__members__.values()))
    for rng in ranges:
        _deliver_range_lists(rng, range_participants[rng], writer)

    _deliver_all_groups(range_participants, writer)

    for rng in ranges:
        _deliver_range_pairs(rng, duels[rng], writer)
    deliver_sorted_pairs(duels, writer)
    for rng in ranges:
        _deliver_range_results(rng, duels[rng], range_participants[rng], writer)

    writer.close()


def _get_participants_per_range(
        duels: dict[Range, list[Duel]]
) -> dict[str, list[Participant]]:
    result = {}

    for rng in duels:
        participants = [d.left for d in duels[rng]] + [d.right for d in duels[rng]]
        participants = list(sorted(set(participants)))
        result[rng] = participants

    return result


def _deliver_participants(
        participants: typing.Iterable[Participant], excel_writer: pd.ExcelWriter
):
    df = (
        pd.DataFrame(
            [
                {
                    "name": p.name,
                    "class": _render_class(p),
                }
                for p in participants
            ]
        )
        .sort_values(
            [
                "class",
                "name",
            ]
        )
        .set_index("class", drop=True)
    )

    df["counts"] = df.groupby(
        [
            "class",
        ]
    ).count()
    df = df.reset_index().set_index(["class", "counts"])
    df = df.rename(
        columns={
            "name": "Імʼя",
            "class": "Клас",
        }
    )
    # cnt = df.groupby(["class", ]).count()
    header_text = "Загальний список"
    sheet_name = header_text
    _add_sheet_header(excel_writer, header_text, sheet_name, 3)

    df.to_excel(
        excel_writer,
        sheet_name=sheet_name,
        # index=False,
        merge_cells=True,
        startrow=2,
    )
    worksheet: xlsxwriter.worksheet.Worksheet = excel_writer.sheets[sheet_name]
    worksheet.autofit()


def _deliver_range_lists(
        rng: Range,
        participants: typing.Iterable[Participant],
        excel_writer: pd.ExcelWriter,
):
    df = (
        pd.DataFrame(
            [
                {
                    "name": p.name,
                    "class": _render_class(p),
                }
                for p in participants
            ]
        )
        .sort_values(["class", "name"])
        .reset_index(drop=True)
    )
    df.index = df.index + 1
    # df = df[["No.", "class", "name"]]

    sheet_name = _sheet_name_range_list(rng)
    header_text = f"Рубіж №{rng.value}"
    _add_sheet_header(excel_writer, header_text, sheet_name, 3)

    df.to_excel(
        excel_writer,
        sheet_name=sheet_name,
        header=False,
        startrow=1,
    )
    worksheet: xlsxwriter.worksheet.Worksheet = excel_writer.sheets[sheet_name]
    worksheet.autofit()


def _deliver_range_pairs(
        range: Range, duels: typing.Iterable[Duel], excel_writer: pd.ExcelWriter
):
    df = (
        pd.DataFrame(
            [
                {
                    "class": _render_class(duel.left),
                    "left": duel.left.name,
                    "_": " " * 16,
                    "right": duel.right.name,
                    "__": " " * 16,
                }
                for duel in duels
            ]
        )
        .sort_values(
            [
                "class",
                "left",
                "right",
            ]
        )
        .reset_index(drop=True)
    )
    df.index = df.index + 1

    sheet_name = f"Пари Рубіж №{range.value}"
    header_text = sheet_name
    _add_sheet_header(excel_writer, header_text, sheet_name, 6)
    df.to_excel(
        excel_writer,
        sheet_name=sheet_name,
        header=False,
        startrow=1,
    )
    worksheet: xlsxwriter.worksheet.Worksheet = excel_writer.sheets[sheet_name]
    worksheet.autofit()


def _deliver_all_groups(
        range_participants: dict[str, list[Participant]], excel_writer: pd.ExcelWriter
):
    range_classes = {
        rng: {p.clazz for p in participants}
        for rng, participants in range_participants.items()
    }
    repeated_classes = [
        c
        for c in Class.__members__.values()
        if c in range_classes[Range.First] and c in range_classes[Range.Second]
    ]
    for clazz in repeated_classes:
        groups = {
            rng: [p for p in participants if p.clazz == clazz]
            for rng, participants in range_participants.items()
        }
        _deliver_groups(groups[Range.First], groups[Range.Second], excel_writer)


def _deliver_groups(
        group_1: list[Participant], group_2: list[Participant], excel_writer
):
    dataframes = [
        pd.DataFrame({"group": f"Група №{idx + 1}", "name": [p.name for p in queue]})
        for idx, queue in enumerate([group_1, group_2])
    ]
    df = pd.concat(dataframes)
    df = df.reset_index()
    df.index = df.index + 1
    df = df.set_index(
        [
            "group",
            "index",
        ]
    )

    sheet_name = f"Групи {_render_class_ua(group_1[0])}"
    header_text = sheet_name
    _add_sheet_header(excel_writer, header_text, sheet_name, 3)

    df.to_excel(excel_writer, sheet_name=sheet_name, merge_cells=True, startrow=2)
    worksheet: xlsxwriter.worksheet.Worksheet = excel_writer.sheets[sheet_name]
    worksheet.autofit()


def _render_class(p: Participant) -> str:
    if p.clazz == Class.STANDARD_MANUAL:
        return "SM"
    elif p.clazz == Class.OPEN:
        return "O"
    elif p.clazz == Class.MODIFIED:
        return "T"
    elif p.clazz == Class.STANDARD:
        return "S"
    elif p.clazz == Class.STANDARD_LADY:
        return "SL"


def _render_class_ua(p: Participant) -> str:
    if p.clazz == Class.STANDARD_MANUAL:
        return "Стандарт-Мануал"
    elif p.clazz == Class.OPEN:
        return "Відкритий"
    elif p.clazz == Class.MODIFIED:
        return "Тактика"
    elif p.clazz == Class.STANDARD:
        return "Стандарт"
    elif p.clazz == Class.STANDARD_LADY:
        return "Стандарт Леді"


def _add_sheet_header(excel_writer, header_text, sheet_name, width: int):
    workbook: xlsxwriter.Workbook = excel_writer.book
    worksheet: xlsxwriter.worksheet.Worksheet = workbook.add_worksheet(sheet_name)
    excel_writer.sheets[sheet_name] = worksheet
    header_format = workbook.add_format(
        {
            "bold": True,
            "align": "center",
        }
    )
    worksheet.merge_range(0, 0, 0, width - 1, header_text, header_format)
    # header_cell.font = header_font
    # header_cell.alignment = openpyxl.styles.Alignment(horizontal="center")


def _add_sheet_header_openpyxl(excel_writer, header_text, sheet_name, width: int):
    workbook: openpyxl.Workbook = excel_writer.book
    worksheet: openpyxl.worksheet.worksheet.Worksheet = workbook.create_sheet(
        sheet_name
    )
    excel_writer.sheets[sheet_name] = worksheet
    header_font = openpyxl.styles.Font(sz=14, bold=True)
    header_cell = worksheet["A1"]
    worksheet["A1"] = header_text
    worksheet.merge_cells(start_row=1, end_row=1, start_column=1, end_column=width)
    header_cell.font = header_font
    header_cell.alignment = openpyxl.styles.Alignment(horizontal="center")


def _equalize_column_width_openpyxl(excel_writer):
    workbook = excel_writer.book
    for ws in workbook.worksheets:
        worksheet: openpyxl.worksheet.worksheet.Worksheet = ws
        dims = {}
        for row in worksheet.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column_letter] = max(
                        (dims.get(cell.column_letter, 0), len(str(cell.value)))
                    )
        for col, value in dims.items():
            worksheet.column_dimensions[col].width = value + 2


def deliver_sorted_pairs(
        range_queues: dict[Range, list[Duel]], excel_writer: pd.ExcelWriter
):
    for r, q in range_queues.items():
        # delays = get_participant_delays(q)
        q_items = [
            {
                "number": idx + 1,
                "class": _render_class(duel.left),
                "left": duel.left.name,
                "_": " " * 16,
                "right": duel.right.name,
                "__": " " * 16,
            }
            for idx, duel in enumerate(q)
        ]
        df = pd.DataFrame(q_items)

        df_delays = df[["left", "right"]]
        df_delays["n"] = df_delays.index + 1

        sheet_name = _sheet_name_range_pairs(r)
        header_text = sheet_name
        _add_sheet_header(excel_writer, header_text, sheet_name, 6)
        df.to_excel(
            excel_writer,
            sheet_name=sheet_name,
            index=False,
            header=False,
            startrow=1,
        )
        worksheet: xlsxwriter.worksheet.Worksheet = excel_writer.sheets[sheet_name]
        worksheet.autofit()
        worksheet.set_column("D:D", 25)

        # _deliver_range_results(r, q, excel_writer)


def _deliver_range_results(r: Range, queue: list[Duel], participants: list[Participant], writer: pd.ExcelWriter):
    sheet_name = _sheet_name_range_results(r)
    book: xlsxwriter.Workbook = writer.book
    result_sheet = book.add_worksheet(sheet_name)
    validation_rule = {
        'validate': 'integer',
        'criteria': 'between',
        'minimum': 0,
        'maximum': 1,
        'input_title': 'Введіть 1 або 0',
        'input_message': '1 значить "перемога", 0 — "поразка"',
    }
    for row, duel in enumerate(queue):
        result_sheet.write(
            row + 1, 0,
            f"{_render_class(duel.left)} {duel.left}"
        )
        result_sheet.write(
            row + 1, 3,
            f"{_render_class(duel.right)} {duel.right}"
        )
    result_sheet.data_validation(1, 1, len(queue), 2, validation_rule)


    participants = sorted(participants, key=lambda p: (p.clazz, p.name))
    last_class = None
    top_border_format = book.add_format()
    top_border_format.set_top()
    for row, p in enumerate(participants):
        fmt = None
        if p.clazz != last_class:
            fmt = top_border_format
        last_class = p.clazz
        result_sheet.write(
            row + 1, 6,
            f"{_render_class(p)} {p}",
            fmt
        )
        result_sheet.write_formula(
            row+1, 7,
            f"""=SUMIF(A:A, G{row+1}, B:B) + SUMIF(D:D, G{row+1}, C:C)""",
            fmt
        )
    result_sheet.autofit()

    # range_list_sheet: xlsxwriter.worksheet.Worksheet = book.get_worksheet_by_name(_sheet_name_range_list(r))
    # for row in range(1, 25):
    #     col = 3
    #     range_list_sheet.write_formula(
    #         row, col,
    #         f"""=SUMIF('{sheet_name}'!A2:A, C{row+1}&" "&B{row+1}, '{sheet_name}'!B2:B)"""
    #         # f"""=C{row+1}&" "&B{row+1}""",
    #     )


def _sheet_name_range_pairs(r):
    return f"Пари Рубіж {r.value} Сортовані"


def _sheet_name_range_results(r):
    return f"Пари Рубіж {r.value} Відомість"


def _sheet_name_range_list(rng):
    return f"Список Рубіж №{rng.value}"
