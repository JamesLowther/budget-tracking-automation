from gettext import Catalog
import json
import os

class Categorizer:
    def __init__(self, data_type):
        self._data_type = data_type
        self._categories = self.read_category_file()

    def read_category_file(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "categories.json")

        with open(path, "r") as f:
            return json.loads(f.read())

    def categorize(self, data):
        categories = self._categories[self._data_type]

        for row in data:
            vendor = row[1]
            category = self.find_category(vendor, categories)
            row.insert(-1, category)

    def remove_ignored(self, data, print_ignored):
        categories = self._categories[self._data_type]

        indicies_to_remove = []

        for i, row in enumerate(data):
            vendor = row[1]

            ignore = self.check_ignored(vendor, categories)
            if ignore:
                indicies_to_remove.append(i)

        print(f"Ignoring {len(indicies_to_remove)} entries in {self._data_type}.")

        a = 0
        for i in indicies_to_remove:
            if print_ignored:
                print(data[i - a])

            data.pop(i - a)
            a += 1

    def check_ignored(self, vendor, categories):
        for entry in categories["Ignore"]:
            if entry.lower() in vendor.lower():
                return True

        return False

    def find_category(self, vendor, categories):
        for key, value in categories.items():
            for entry in value:
                if entry.lower() in vendor.lower():
                    return key

        return "Other"
