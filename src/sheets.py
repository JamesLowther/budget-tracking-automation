from dataclasses import dataclass
import pygsheets
import os
from datetime import datetime

from sorting import sort
from filtering import filter_before_cutoff

class SheetsAPI:
    SHEET = "Budget Tracking Tool"
    EXPENSES_WORKSHEET = "Expenses"
    INCOME_WORKSHEET = "Income"

    DATA_OFFSET = 7

    _gc = None
    _sh = None

    def __init__(self, data_type):
        self._data_type = data_type

        if SheetsAPI._gc is None:
            print(f"Pulling data from {SheetsAPI.SHEET}... ", end="", flush=True)

            token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
            SheetsAPI._gc = pygsheets.authorize(service_account_file=token_path)
            SheetsAPI._sh = self._gc.open(SheetsAPI.SHEET)

            print("Done.")

        self._wks = None

        title = SheetsAPI.EXPENSES_WORKSHEET if self._data_type == "withdrawls" else SheetsAPI.INCOME_WORKSHEET
        for wks in self._sh:
            if wks.title == title:
                self._wks = wks

        self._cutoff_offset = None
        self._insert_row = None

        self._data = self.initialize_data()

    def initialize_data(self):
        data = list(self._wks)[SheetsAPI.DATA_OFFSET:]

        formatted_data = []

        for d in data:
            comment = ""
            if d[5].lower() == "manual":
                comment = "manual"

            formatted_data.append(
                (
                    d[1],                                               # Date.
                    d[2],                                               # Vendor.
                    d[3].lstrip("$").replace(",", "").strip(" "),       # Price.
                    comment                                             # Comment.
                )
            )

        filtered_formatted_data = filter_before_cutoff(formatted_data)

        self._cutoff_offset = len(formatted_data) - len(filtered_formatted_data)

        return filtered_formatted_data

    def format_data(self, data):
        data_temp = []

        for d in data:
            data_temp.append(
                (
                    d[0],
                    d[1],
                    d[2],
                    ""
                )
            )

        return set(data_temp)

    def set_insert_row(self, new_data, merged_data):
        smallest_date = datetime.strptime(new_data[0][0], "%m-%d-%Y")

        i = 0
        for d in merged_data:
            d_date = datetime.strptime(d[0], "%m-%d-%Y")

            if d_date > smallest_date:
                print("WHAT!")
                exit(1)

            elif d_date == smallest_date:
                break
            i += 1

        self._insert_row = SheetsAPI.DATA_OFFSET + self._cutoff_offset + i + 1

        return merged_data[i:]

    def merge(self, data):
        print(f"Merging {self._data_type}... ", end="")

        data_set = self.format_data(data)
        sheet_set = set(self._data)

        new_data = list(data_set - sheet_set)
        sort(new_data)

        merged_data = list(data_set.union(sheet_set))
        sort(merged_data)

        new_indexes = []

        if new_data != []:
            merged_data = self.set_insert_row(new_data, merged_data)

            for row in new_data:
                new_indexes.append(merged_data.index(row))

        merged_data = [list(x) for x in merged_data]

        print("Done.")

        return (merged_data, new_indexes)

    def upload(self, data):
        print(f"\nStarting insert at row {self._insert_row}.")
        print(f"Uploading {self._data_type}... ", end="", flush=True)

        i = 0
        for row in data:
            self._wks.update_row(
                self._insert_row + i,
                row,
                col_offset = 1
            )
            i += 1

        print("Done.")
