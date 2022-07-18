from gettext import Catalog
import json
import os

class Categorizer:
    def __init__(self):
        self._categories = self.read_category_file()

    def read_category_file(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "categories.json")

        with open(path, "r") as f:
            return json.loads(f.read())

    def categorize(self, data, data_type="withdrawls"):
        categories = self._categories["withdrawls"]
        if data_type == "deposits":
            categories = self._categories["deposits"]

        for row in data:
            vendor = row[1]
            category = self.find_category(vendor, categories)
            row.append(category)

    def remove_ignored(self, data, data_type="withdrawls"):
        categories = self._categories["withdrawls"]
        if data_type == "deposits":
            categories = self._categories["deposits"]

        indicies_to_remove = []

        for i, row in enumerate(data):
            vendor = row[1]

            ignore = self.check_ignored(vendor, categories)
            if ignore:
                indicies_to_remove.append(i)

        a = 0
        for i in indicies_to_remove:
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
