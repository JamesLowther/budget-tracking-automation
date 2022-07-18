import argparse
from html import entities
from sheets import SheetsAPI

from td import TDReader
from categorize import Categorizer
from filtering import filter_before, filter_after
from editing import edit

parser = argparse.ArgumentParser(description='Process entries from bank statements.')
parser.add_argument('-b', "--before", type=str, help="Only process entries before a certain date (MM-DD-YYYY). Default: none", default="")
parser.add_argument('-a', "--after", type=str, help="Only process entries after a certain date (MM-DD-YYYY). Default: none", default="")
args = parser.parse_args()

def main():
    e = TDReader()
    withdrawls, deposits = e.get_data()

    if args.after != "":
        withdrawls, deposits = filter_after(args.after, withdrawls, deposits)

    if args.before != "":
        withdrawls, deposits = filter_before(args.before, withdrawls, deposits)

    c = Categorizer()
    c.remove_ignored(withdrawls, data_type="withdrawls")
    c.remove_ignored(deposits, data_type="deposits")

    sheets = SheetsAPI()

    withdrawls, new_withdrawl_indexes = sheets.merge(withdrawls, data_type="withdrawls")
    deposits, new_deposit_indexes = sheets.merge(deposits, data_type="deposits")

    print()

    if new_withdrawl_indexes:
        c.categorize(withdrawls, data_type="withdrawls")
        edit(withdrawls, new_withdrawl_indexes, data_type="withdrawls")

        print(f"{len(new_withdrawl_indexes)} entries to add to expenses.")

    else:
        print("Nothing to add to expenses.")

    if new_deposit_indexes:
        c.categorize(deposits, data_type="deposits")
        edit(deposits, new_deposit_indexes, data_type="deposits")

        print(f"{len(new_deposit_indexes)} entries to add to income.")

    else:
        print("Nothing to add to income.")

    if input("\nContinue adding to sheet? [y/N]: ").lower() == "y":
        sheets.upload(withdrawls, data_type="withdrawls")
        sheets.upload(deposits, data_type="deposits")

if __name__ == "__main__":
    main()
