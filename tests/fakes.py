from __future__ import annotations

import csv
import json
import os.path
import re
import string
# from functools import cache
from pathlib import Path
from typing import Union, cast

from typing import TYPE_CHECKING

# import numpy

from mlbstandings.helpers import sheet_range_to_rc0_range

if TYPE_CHECKING:
    from mlbstandings.shared_types import *
    from typing import Dict, List
    from mlbstandings.typing_protocols import *


class FakeDrive:
    def __init__(self, directory: Dict[str, Path]) -> None:
        self.directory = directory

    def get_spreadsheet_id(self, name: str) -> str:
        return str(self.directory[name])


def sheet_coltoindex(col: str) -> int:
    """https://stackoverflow.com/a/12640614"""
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num - 1


class FakeSheet:
    def __init__(self, values: SheetArray):
        print(f'values={values}')
        self.col_count = len(values[0]) if len(values) > 0 else 0
        for row in values[1:]:
            if len(row) != self.col_count:
                raise ValueError('Mismatched row lengths')
        self.values = values

    @staticmethod
    def convert_cell(cell: str) -> Union[str, int]:
        return int(cell) if cell.isnumeric() else cell

    @staticmethod
    def fromcsv(csvpath: Path) -> FakeSheet:
        with open(csvpath, newline='') as f:
            return FakeSheet([[FakeSheet.convert_cell(v) for v in x] for x in csv.reader(f)])

    def tocsv(self, csvpath: Path) -> None:
        with open(csvpath, 'w', newline='') as f:
            csv.writer(f).writerows(self.values)

    # @cache
    # def transposed_values(self) -> SheetArray:
    #     return numpy.transpose(self.values)

    def read_values(self, sheet_range: str, major_dimension: Dimension) -> SheetArray:
        rc0_range = sheet_range_to_rc0_range(sheet_range)
        print(f'{rc0_range=}')
        # if major_dimension == 'COLUMNS':
        #     vals = self.transposed_values()
        #     rc0_range = tuple(tuple(reversed(cell)) for cell in rc0_range)
        # else:
        #     vals = self.values()
        # print(vals)
        # # This may not mimic sheets behavior exactly but whatever
        # fancy_range = (
        #     (
        #         0 if rc0_range[0][0] == -1 else rc0_range[0][0],
        #         idunno
        #     ),
        #     (
        #         len(vals) if rc0_range[1][0] == -1 else rc0_range[1][0],
        #         idunno
        #     )
        # )
        # print(fancy_range)
        input_row_start = rc0_range[0][0] if rc0_range[0][0] != - 1 else 0
        input_row_limit = rc0_range[1][0] - 1 if rc0_range[1][0] != -1 else len(self.values)
        input_col_start = rc0_range[0][1] if rc0_range[0][1] != - 1 else 0
        input_col_limit = rc0_range[1][0] -1 if rc0_range[1][0] != -1 else self.col_count
        print(f'{input_row_start=} {input_row_limit=}')
        print(f'{input_col_start=} {input_col_limit=}')
        out_rows, out_cols = input_row_limit - input_row_start, input_col_limit - input_col_start
        if major_dimension == 'COLUMNS':
            out_rows, out_cols = out_cols, out_rows
        result = [ [''] * out_cols for i in range(out_rows) ]
        raise NotImplementedError(f'read_values({sheet_range}, {major_dimension})')

    def write_values(self, sheet_range: str, values: SheetArray, major_dimension: Dimension) -> None:
        raise NotImplementedError('oop')


class FakeSpreadsheet:
    def __init__(self, test_data_dir: Path, spreadsheet_id: str) -> None:
        self.test_data_dir = test_data_dir
        self.id = spreadsheet_id
        with (self.test_data_dir / 'named_ranges.json').open() as nr:
            self.named_ranges = json.load(nr)
        print(self.named_ranges)
        self.sheets = {
            os.path.splitext(fpath.name)[0]: FakeSheet.fromcsv(fpath)
            for fpath in self.test_data_dir.glob('*.csv')
        }
        print(self.sheets)

    def close(self) -> None:
        with (self.test_data_dir / 'named_ranges.json').open('w') as nr:
            json.dump(self.named_ranges, nr)
        for sheet_name, sheet in self.sheets.items():
            sheet.tocsv(self.test_data_dir / f'{sheet_name}.csv')

    def get_named_cell(self, name: str) -> Union[str, int]:
        result = self.named_ranges[name]
        if type(result) not in [str, int]:
            raise TypeError(f'{result} has wrong type {type(result)}')
        return cast(Union[str, int], result)

    def set_named_cell(self, name: str, value: Union[str, int]) -> None:
        self.named_ranges[name] = value

    def read_values(self, sheet_name: str, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        print(f'read_values(sheet_name={sheet_name}, sheet_range={sheet_range}')
        return self.sheets[sheet_name].read_values(sheet_range, major_dimension)

    def get_range(self, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        message = f'get_range(sheet_sheet_range={sheet_range}'
        print(message)
        n, r = sheet_range.split('!', 1)
        return self.read_values(n, r, major_dimension)

    def write_values(self, sheet_name: str, sheet_range: str, values: SheetArray, major_dimension: Dimension = 'ROWS') -> None:
        self.sheets[sheet_name].write_values(sheet_range, values, major_dimension)


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


# # TODO maybe delete. handy for figuring out type complaints.
# def ok() -> SpreadsheetLike:
#     return FakeSpreadsheet(Path(''), '')
#
#
# def ok2() -> SpreadsheetLike:
#     scopes = ['https://www.googleapis.com/auth/spreadsheets',
#               'https://www.googleapis.com/auth/drive.metadata.readonly']
#     creds = google.auth.default(scopes=scopes)[0]
#     spreadsheets = mlbstandings.google_wrappers.Spreadsheets(creds)
#     return spreadsheets.spreadsheet('')
