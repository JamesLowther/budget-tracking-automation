import csv
import os
from datetime import datetime
class TDReader:
    FILE_PATH = "../files"
    def get_data(self):
        all_files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.FILE_PATH))

        all_withdrawls = []
        all_deposits = []

        for name in all_files:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.FILE_PATH, name)
            if os.path.isfile(path) and name.split(".")[-1] == "csv":
                withdrawls, deposits = self.read_csv(path)

                all_withdrawls += withdrawls
                all_deposits += deposits

        all_withdrawls.sort(key=lambda x: datetime.strptime(x[0], "%m-%d-%Y"))
        all_deposits.sort(key=lambda x: datetime.strptime(x[0], "%m-%d-%Y"))

        return (all_withdrawls, all_deposits)

    def read_csv(self, path):
        with open(path, "r") as f:
            data = list(csv.reader(f))
            withdrawls, deposits = self.format_data(data)

            return (withdrawls, deposits)

    def format_data(self, data):
        withdrawls = []
        deposits = []

        for row in data:
            temp = [
                row[0].replace("/", "-"),
                " ".join(row[1].split())
            ]

            if row[2] != "":
                temp.append(row[2])
                withdrawls.append(temp)

            else:
                temp.append(row[3])
                deposits.append(temp)

        return (withdrawls, deposits)
