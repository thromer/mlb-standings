from __future__ import annotations

import json
import re
from pathlib import Path
# noinspection PyUnresolvedReferences
from typing import Union, Dict, List, cast
# noinspection PyUnresolvedReferences
from mlbstandings.typing_protocols import *
from mlbstandings.shared_types import *


class FakeDrive:
    def __init__(self, directory: Dict[str, Path]) -> None:
        self.directory = directory

    def get_spreadsheet_id(self, name: str) -> str:
        return str(self.directory[name])


class FakeSpreadsheet:
    def __init__(self, test_data_dir: Path, spreadsheet_id: str) -> None:
        self.test_data_dir = test_data_dir
        self.id = spreadsheet_id
        with (self.test_data_dir / 'named_ranges.json').open() as nr:
            self.named_ranges = json.load(nr)
        print(self.named_ranges)

    @staticmethod
    def convert_cell(cell: str) -> Union[str, int]:
        return int(cell) if cell.isnumeric() else cell

    def close(self) -> None:
        with (self.test_data_dir / 'named_ranges.json').open('w') as nr:
            json.dump(self.named_ranges, nr)

    # def sheet(self, name: str) -> SheetLike:
    #     raise NotImplementedError()

    def get_named_cell(self, name: str) -> Union[str, int]:
        result = self.named_ranges[name]
        if type(result) not in [str, int]:
            raise TypeError(f'{result} has wrong type {type(result)}')
        return cast(Union[str, int], result)

    def set_named_cell(self, name: str, value: Union[str, int]) -> None:
        self.named_ranges[name] = value

    def read_values(self, sheet_name: str, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        print(f'read_values(sheet_name={sheet_name}, sheet_range={sheet_range}')
        return [[]]
        # raise NotImplementedError(message)

    def get_range(self, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        message = f'get_range(sheet_sheet_range={sheet_range}'
        print(message)
        return [[]]
        # raise NotImplementedError(message)


class FakeSpreadsheets:
    def __init__(self, test_data_dir: Path) -> None:
        self.test_data_dir = test_data_dir
        self.spreadsheets: List[FakeSpreadsheet] = []

    def close(self) -> None:
        for ss in self.spreadsheets:
            ss.close()

    def spreadsheet(self, spreadsheet_id: str) -> FakeSpreadsheet:
        ss = FakeSpreadsheet(self.test_data_dir, spreadsheet_id)
        self.spreadsheets.append(ss)
        return ss


class FakeWeb:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def read(self, url: str) -> str:
        print(url)
        fname = None
        if url == 'https://www.baseball-reference.com/leagues/majors/2023-schedule.shtml':
            fname = f'{self.data_dir}/{url.split("/")[-1]}'
        else:
            m = re.match(
                r'https://www.baseball-reference.com/boxes/\?year=(\d{4})&month=(\d{2})&day=(\d{2})', url)
            if m:
                fname = f'{self.data_dir}/boxes-{m[1]}-{m[2]}-{m[3]}.html'

        if fname is None:
            raise ValueError(f'{url} unsupported by FakeWeb')

        print(fname)
        with open(fname) as f:
            return f.read()
