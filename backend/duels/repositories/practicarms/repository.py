import asyncio

import aiohttp
import bs4
from bs4 import BeautifulSoup

import duels.api_models
import duels.model


class PracticarmsRepository:

    @staticmethod
    def clazz(class_name: str, category_name) -> duels.model.Class:
        mapping = {
            "Стандарт": duels.model.Class.STANDARD,
            "Стандарт-мануал": duels.model.Class.STANDARD_MANUAL,
            "Модифікований": duels.model.Class.MODIFIED,
            "Відкритий": duels.model.Class.OPEN,
        }
        clazz = mapping[class_name]
        if clazz == duels.model.Class.STANDARD and category_name == "Леді":
            clazz = duels.model.Class.STANDARD_LADY
        return clazz

    async def load(self, url: str) -> duels.api_models.MatchSetup:
        parsed_webpage = await self._fetch_webpage(url)
        participants = await self._parse_participants(parsed_webpage)
        return await self._build_match_setup(participants)

    async def _fetch_webpage(self, url) -> bs4.BeautifulSoup:
        async with aiohttp.ClientSession() as session:
            response = await session.get(url)
            body = await response.text(errors='replace')
        parsed_webpage = BeautifulSoup(
            body,
            parser='html.parser',
        )
        return parsed_webpage

    async def _parse_participants(self, parsed_webpage) -> list[dict]:
        participants = list()
        table_participants = parsed_webpage.find('div', class_='table participants_list')
        # print(table_participants.prettify())
        rows = table_participants.find_all('div', class_='participant')
        for row in rows:
            cells = row.find_all('div', class_='cell')
            values = list()
            for cell in cells:
                span_desktop = cell.find('span', class_='desctop')
                if span_desktop:
                    text = span_desktop.text
                else:
                    text = cell.text
                values.append(text)
            cell_meanings = [None, None, "name", "squad", None, "category", "clazz"]
            participant = {
                meaning: cell_value
                for meaning, cell_value in zip(cell_meanings, values)
                if meaning
            }
            participant["clazz"] = self.clazz(participant["clazz"], participant["category"])
            participants.append(participant)
        return participants

    async def _build_match_setup(self, participants) -> duels.api_models.MatchSetup:
        all_classes = {p["clazz"] for p in participants}
        result = duels.api_models.MatchSetup(
            ranges={
                duels.model.Range.First: duels.api_models.RangeSetup(
                    classes={
                        clazz: duels.api_models.ClassSetup(
                            participants=[p["name"] for p in participants if p["clazz"] == clazz],
                            times=1,
                        )
                        for clazz in all_classes
                    }
                ),
                duels.model.Range.Second: duels.api_models.RangeSetup(classes={}),
            }
        )
        return result


def main():
    async def _main():
        url = "https://practicarms.ua/event-5897-participants-duelnii-kubok-bandershtadtu-2024.html"
        duels = await PracticarmsRepository().load(url)
        # print()

    asyncio.run(_main())


if __name__ == '__main__':
    main()