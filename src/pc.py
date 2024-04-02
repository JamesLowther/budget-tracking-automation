import csv
import os

from sorting import sort

class PCReader:
    FILE_PATH = "../pc-files"

    def get_data(self):
        print("Reading PC CSV files... ", end="", flush=True)
        all_files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), PCReader.FILE_PATH))

        all_withdrawls = []
        all_deposits = []

        for name in all_files:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), PCReader.FILE_PATH, name)
            if os.path.isfile(path) and name.split(".")[-1] == "csv":
                withdrawls, deposits = self.read_csv(path)

                all_withdrawls += withdrawls
                all_deposits += deposits

        sort(all_withdrawls)
        sort(all_deposits)

        print("Done.")

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
            if row[0] == "Description":
                continue

            temp = [
                row[3].replace("/", "-"),
                " ".join(row[0].split()).replace(",", "")
            ]

            if row[1] == "PURCHASE":
                temp.append("{0:.2f}".format(abs(float(row[5]))))
                withdrawls.append(temp)

        return (withdrawls, deposits)
