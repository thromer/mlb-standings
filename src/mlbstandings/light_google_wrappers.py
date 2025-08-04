from __future__ import annotations

from typing import Any, Callable, TypeVar, cast, final
from urllib.parse import quote  # TODO remove probably

import backoff
from requests.exceptions import HTTPError, Timeout
from requests.sessions import Session

from mlbstandings.shared_types import Dimension, SheetArray, SheetValue


_CallableT = TypeVar("_CallableT", bound=Callable[..., Any])


def backoff_on_retryable() -> Callable[[_CallableT], _CallableT]:
    return backoff.on_exception(
        backoff.expo,
        (HTTPError, Timeout),
        max_time=600,
        giveup=lambda e: isinstance(e, HTTPError)
        and e.response.status_code not in set([429, 500, 503]),
        max_value=60,
    )


@final
class Spreadsheet:
    def __init__(self, session: Session, spreadsheet_id: str) -> None:
        self.session = session
        self.id = spreadsheet_id

    def close(self) -> None:
        return None

    # @backoff_on_retryable()
    def set_range(self, range_str: str, values: SheetArray) -> None:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.id}/values/{quote(range_str)}"
        params = {
            "valueInputOption": "RAW",
            "includeValuesInResponse": "false",
            "alt": "json",
        }
        # print(f'PUT {url}')
        resp = self.session.put(url, params=params, json={"values": values})
        resp.raise_for_status()

    def set_cell(self, cell_str: str, value: SheetValue) -> None:
        self.set_range(cell_str, [[value]])

    # @backoff_on_retryable()
    def get_range(
        self, range_str: str, major_dimension: Dimension = "ROWS"
    ) -> SheetArray:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.id}/values/{quote(range_str)}"
        params = {
            "majorDimension": major_dimension,
            "valueRenderOption": "UNFORMATTED_VALUE",
            "dateTimeRenderOption": "SERIAL_NUMBER",
        }
        # print(f'GET {url}')
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return cast(SheetArray, resp.json().get("values", [[]]))

    def get_cell(self, cell_str: str) -> SheetValue:
        range_values = self.get_range(cell_str)
        if len(range_values) == 0 or len(range_values[0]) == 0:
            return ""
        return range_values[0][0]

    # @backoff_on_retryable()
    def append_to_range(self, range_str: str, values: SheetArray) -> dict[str, Any]:
        url = f"https://content-sheets.googleapis.com/v4/spreadsheets/{self.id}/values/{quote(range_str)}:append"
        params = {
            "valueInputOption": "USER_ENTERED",
            "includeValuesInResponse": "false",
            "alt": "json",
        }
        # print(f'POST {url}')
        resp = self.session.post(url, params=params, json={"values": values})
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())

    # @backoff_on_retryable()
    def clear_range(self, range_str: str) -> None:
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.id}/values/{quote(range_str)}:clear"
        # print(f'POST {url}')
        resp = self.session.post(url)
        resp.raise_for_status()

    def clear_sheet(self, sheet_name: str) -> None:
        append_res = self.append_to_range(f"'{sheet_name}'!A1:A", [[""]])
        clear_range = append_res["updates"]["updatedRange"].replace("!A", "!1:", 1)
        self.clear_range(clear_range)


@final
class Spreadsheets:
    def __init__(self, session: Session) -> None:
        self.session = session

    def close(self) -> None:
        # self.session.close()
        return None

    def spreadsheet(self, spreadsheet_id: str) -> Spreadsheet:
        return Spreadsheet(self.session, spreadsheet_id)


@final
class Files:
    def __init__(self, session: Session) -> None:
        self.session = session

    @backoff_on_retryable()
    def copy(self, id: str, name: str) -> str:
        url = f"https://content.googleapis.com/drive/v3/files/{id}/copy"
        params = {"alt": "json"}
        resp = self.session.post(url, params=params, json={"name": name})
        resp.raise_for_status()
        return cast(str, resp.json()["id"])
