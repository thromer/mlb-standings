from __future__ import annotations

import csv
import json
import os.path
import re
import string

from pathlib import Path
from mlbstandings.helpers import sheet_range_to_rc0_range
from mlbstandings.shared_types import SheetValue
# noinspection PyUnresolvedReferences
from mlbstandings.shared_types import SheetArray

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from mlbstandings.shared_types import *
    from typing import Any, List
    from mlbstandings.typing_protocols import *


def _convert_cell(cell: Any) -> SheetValue:
    if type(cell) is int:
        return int(cell)
    if type(cell) is str:
        return int(cell) if cell.isnumeric() else cell
    raise TypeError(f'cell has unexpected type {type(cell)}')


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
        self.c_min = 0
        self.r_min = 0
        self.r_max = len(values) - 1
        self.c_max = len(values[0]) - 1 if len(values) > 0 else -1
        print(f'{self.r_min=} {self.r_max=}')
        print(f'{self.c_min=} {self.c_max=}')
        for row in values[1:]:
            if len(row) != self.c_max + 1:
                raise ValueError('Mismatched row lengths')
        self.values = values

    @staticmethod
    def fromcsv(csvpath: Path) -> FakeSheet:
        with open(csvpath, newline='') as f:
            return FakeSheet([[_convert_cell(v) for v in x] for x in csv.reader(f)])

    def tocsv(self, csvpath: Path) -> None:
        with open(csvpath, 'w', newline='') as f:
            csv.writer(f, lineterminator='\n').writerows(self.values)

    # @cache
    # def transposed_values(self) -> SheetArray:
    #     return numpy.transpose(self.values)

    def read_values(self, sheet_range: str, major_dimension: Dimension) -> SheetArray:
        rc0_range = sheet_range_to_rc0_range(sheet_range)
        print(f'{rc0_range=}')
        r_min = rc0_range[0][0] if rc0_range[0][0] != -1 else self.r_min
        r_max = rc0_range[1][0] if rc0_range[1][0] != -1 else self.r_max
        c_min = rc0_range[0][1] if rc0_range[0][1] != -1 else self.c_min
        c_max = rc0_range[1][1] if rc0_range[1][1] != -1 else self.c_max
        print(f'{r_min=} {r_max=}')
        print(f'{c_min=} {c_max=}')
        if r_max < r_min or c_max < c_min:
            result: SheetArray = [[]]
            print(f'read_values({sheet_range} {major_dimension})={result}')
        out_rows, out_cols = r_max - r_min + 1, c_max - c_min + 1
        if major_dimension == 'COLUMNS':
            out_rows, out_cols = out_cols, out_rows
        print(f'{out_rows=} {out_cols=}')
        result = [[''] * out_cols for _ in range(out_rows)]
        print(f'{result=}')
        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                out_r, out_c = r - r_min, c - c_min
                if major_dimension == 'COLUMNS':
                    out_r, out_c = out_c, out_r
                result[out_r][out_c] = self.values[r][c]
        print(f'read_values({sheet_range} {major_dimension})={result}')
        return result

    @staticmethod
    def transpose(values: SheetArray) -> SheetArray:
        n_rows = len(values)
        if n_rows == 0:
            return values
        n_columns = len(values[0])
        for col in values[1:]:
            if len(col) != n_columns:
                raise ValueError(f'{values} is not rectangular')
        result = [[_convert_cell('')] * n_rows for _ in range(n_columns)]
        print(f'{n_rows=} {n_columns=}')
        print(f'transpose({values} intermediate {result=}')
        for r in range(0, n_columns):
            for c in range(0, n_rows):
                print(f'{r=} {c=}')
                result[r][c] = values[c][r]
        print(f'transpose({values})={result}')
        return result

    def write_values(self, sheet_range: str, values: SheetArray, major_dimension: Dimension) -> None:
        print(f'write_values({sheet_range}, {values}, {major_dimension}')
        if major_dimension == 'COLUMNS':
            values = self.transpose(values)
        rc0_range = sheet_range_to_rc0_range(sheet_range)
        print(f'{rc0_range=}')
        r_min = rc0_range[0][0] if rc0_range[0][0] != -1 else self.r_min
        r_max = rc0_range[1][0] if rc0_range[1][0] != -1 else self.r_max
        c_min = rc0_range[0][1] if rc0_range[0][1] != -1 else self.c_min
        c_max = rc0_range[1][1] if rc0_range[1][1] != -1 else self.c_max
        print(f'{r_min=} {r_max=}')
        print(f'{c_min=} {c_max=}')
        out_rows, out_cols = r_max - r_min + 1, c_max - c_min + 1
        print(f'{out_rows=} {out_cols=}')
        # if ((out_rows == 0 and len(values) > 0) or
        #         out_rows != len(values) or
        #         out_cols != len(values[0])):
        #     raise ValueError(f'write_values range and values are different dimensions')

        if self.r_max < r_max:
            self.values.extend([[''] * (self.c_max + 1) for _ in range(r_max - self.r_max)])
            self.r_max = r_max
        if self.c_max < c_max:
            for row in self.values:
                row.extend([''] * (c_max - self.c_max))
            self.c_max = c_max
        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                in_r, in_c = r - r_min, c - c_min
                if major_dimension == 'COLUMNS':
                    in_r, in_c = in_c, in_r
                self.values[r][c] = values[in_r][in_c]
        print(f'{self.values=}')


class FakeSpreadsheet:
    def __init__(self, test_data_dir: Path, spreadsheet_id: str) -> None:
        self.data_dir = test_data_dir / spreadsheet_id
        with (self.data_dir / 'named_ranges.json').open() as nr:
            self.named_ranges = json.load(nr)
        print(self.named_ranges)
        self.sheets = {
            os.path.splitext(fpath.name)[0]: FakeSheet.fromcsv(fpath)
            for fpath in self.data_dir.glob('*.csv')
        }
        print(self.sheets)

    def close(self) -> None:
        with (self.data_dir / 'named_ranges.json').open('w') as nr:
            json.dump(self.named_ranges, nr)
        for sheet_name, sheet in self.sheets.items():
            sheet.tocsv(self.data_dir / f'{sheet_name}.csv')

    def get_named_range(self, name: str) -> SheetArray:
        return cast(SheetArray, self.named_ranges[name])

    def set_named_range(self, name: str, arr: SheetArray) -> None:
        self.named_ranges[name] = arr

    def get_named_cell(self, name: str) -> SheetValue:
        return _convert_cell(self.get_named_range(name)[0][0])

    def set_named_cell(self, name: str, value: SheetValue) -> None:
        self.named_ranges[name] = [[value]]

    def read_values(self, sheet_name: str, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        print(f'read_values(sheet_name={sheet_name}, sheet_range={sheet_range}')
        return self.sheets[sheet_name].read_values(sheet_range, major_dimension)

    def get_range(self, sheet_range: str, major_dimension: Dimension = 'ROWS') -> SheetArray:
        message = f'get_range(sheet_sheet_range={sheet_range}'
        print(message)
        n, r = sheet_range.split('!', 1)
        return self.read_values(n, r, major_dimension)

    def write_values(self, sheet_name: str, sheet_range: str,
                     values: SheetArray, major_dimension: Dimension = 'ROWS') -> None:
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
