import argparse
from sheets import SheetsAPI

from td import TDReader
from categorize import Categorizer
from filtering import filter_before, filter_after, filter_before_cutoff
from editing import edit

parser = argparse.ArgumentParser(description='Process entries from bank statements.')
parser.add_argument('-b', "--before", type=str, help="Only process entries before a certain date (MM-DD-YYYY). Default: none", default="")
parser.add_argument('-a', "--after", type=str, help="Only process entries after a certain date (MM-DD-YYYY). Default: none", default="")
parser.add_argument('-s', "--skip", type=str, help="Skip a data type. Either expenses or income. Default: none", default="")
args = parser.parse_args()

def main():
    e = TDReader()
    withdrawls, deposits = e.get_data()

    withdrawls = filter_before_cutoff(withdrawls)
    deposits = filter_before_cutoff(deposits)

    if args.after != "":
        withdrawls, deposits = filter_after(args.after, withdrawls, deposits)

    if args.before != "":
        withdrawls, deposits = filter_before(args.before, withdrawls, deposits)

    withdrawls_c = Categorizer("withdrawls")
    deposits_c = Categorizer("deposits")

    withdrawls_c.remove_ignored(withdrawls)
    deposits_c.remove_ignored(deposits)

    withdrawls_sheets = SheetsAPI("withdrawls")
    deposits_sheets = SheetsAPI("deposits")

    withdrawls, new_withdrawl_indexes = withdrawls_sheets.merge(withdrawls)
    deposits, new_deposit_indexes = deposits_sheets.merge(deposits)

    print()

    upload_withdrawls = False
    if not args.skip == "expenses":
        if new_withdrawl_indexes:
            withdrawls_c.categorize(withdrawls)
            edit(withdrawls, new_withdrawl_indexes, data_type="withdrawls")

            upload_withdrawls = True

            print(f"{len(new_withdrawl_indexes)} entries to add to expenses.")

        else:
            print("Nothing to add to expenses.")
    else:
        print("Skipping expenses.")

    upload_deposits = False
    if not args.skip == "income":
        if new_deposit_indexes:
            deposits_c.categorize(deposits)
            edit(deposits, new_deposit_indexes, data_type="deposits")

            upload_deposits = True

            print(f"{len(new_deposit_indexes)} entries to add to income.")

        else:
            print("Nothing to add to income.")
    else:
        print("Skipping income.")

    if (new_withdrawl_indexes or new_deposit_indexes) and input("\nContinue adding to sheet? [y/N]: ").lower() == "y":
        if upload_withdrawls:
            withdrawls_sheets.upload(withdrawls)

        if upload_deposits:
            deposits_sheets.upload(deposits)

if __name__ == "__main__":
    main()
