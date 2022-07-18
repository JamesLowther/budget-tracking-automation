import pygsheets
import os
from datetime import datetime

from sorting import sort

class SheetsAPI:
    SHEET = "Copy of Budget Tracking Tool"
    EXPENSES_WORKSHEET = "Expenses"
    INCOME_WORKSHEET = "Income"

    DATA_OFFSET = 7

    def __init__(self):
        print(f"Pulling data from {self.SHEET}... ", end="", flush=True)

        token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")
        self._gc = pygsheets.authorize(service_account_file=token_path)
        self._sh = self._gc.open(self.SHEET)

        self._expenses_wks = None
        self._income_wks = None

        for wks in self._sh:
            if wks.title == self.EXPENSES_WORKSHEET:
                self._expenses_wks = wks

            if wks.title == self.INCOME_WORKSHEET:
                self._income_wks = wks

            if self._expenses_wks and self._income_wks:
                break

        self._expenses_data = self.initialize_data(self._expenses_wks)
        self._income_data = self.initialize_data(self._income_wks)

        self._expenses_insert_row = None
        self._income_insert_row = None

        print("Done.")

    def initialize_data(self, worksheet):
        data = list(worksheet)[7:]

        formatted_data = []

        for d in data:
            formatted_data.append(
                (
                    d[1],
                    d[2],
                    d[3].lstrip("$").replace(",", "").strip(" ")
                )
            )

        return formatted_data

    def get_data(self, data_type):
        data = []

        if data_type == "withdrawls":
            data = self._expenses_data

        elif data_type == "deposits":
            data = self._income_data

        return data

    def get_last_row(self, data_type="withdrawls"):
        data = self.get_data(data_type)

        if not data:
            return None

        return len(data) + self.DATA_OFFSET


    def match_row(self, row, data_type="withdrawls"):
        data = self.get_data(data_type)

        try:
            i = data.index(tuple(row)[:3])
        except ValueError:
            i = None

        return i

    def set_insert_row(self, row, data_type="withdrawls"):
        if data_type == "withdrawls":
            self._expenses_insert_row = row

        elif data_type == "deposits":
            self._income_insert_row = row

    def merge(self, data, data_type="withdrawls"):
        print(f"Merging {data_type}... ", end="")

        start_match = self.match_row(data[0], data_type=data_type)
        sheet_data = self.get_data(data_type=data_type)

        if start_match is None:
            start_match = len(sheet_data)
            self.set_insert_row(self.get_last_row(data_type=data_type) + 1, data_type=data_type)

        else:
            self.set_insert_row(start_match + self.DATA_OFFSET + 1, data_type=data_type)

        sheet_data = sheet_data[start_match:]

        data_set = set([tuple(x) for x in data])
        sheet_data_set = set(sheet_data)

        newly_added = data_set - sheet_data_set
        newly_added = list(newly_added)
        sort(newly_added)


        merged = data_set.union(sheet_data_set)
        merged = list(merged)
        sort(merged)

        new_indexes = []
        for row in newly_added:
            new_indexes.append(merged.index(row))

        merged = [list(x) for x in merged]

        print("Done.")

        return (merged, new_indexes)

    def upload(self, data, data_type="withdrawls"):
        print(f"Uploading {data_type}... ", end="")

        wks = None
        insert_row = None
        if data_type == "withdrawls":
            wks = self._expenses_wks
            insert_row = self._expenses_insert_row
        elif data_type == "deposits":
            wks = self._income_wks
            insert_row = self._income_insert_row

        i = 0
        for row in data:
            wks.update_row(
                insert_row + i,
                row,
                col_offset = 1
            )
            i += 1

        print("Done.")
