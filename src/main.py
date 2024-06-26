import argparse
from sheets import SheetsAPI

from td import TDReader
from pc import PCReader
from categorize import Categorizer
from filtering import filter_before, filter_after, filter_before_cutoff
from editing import edit
from sorting import sort

parser = argparse.ArgumentParser(description='Process entries from bank statements.')
parser.add_argument('-b', "--before", type=str, help="Only process entries before a certain date (MM-DD-YYYY).", default="")
parser.add_argument('-a', "--after", type=str, help="Only process entries after a certain date (MM-DD-YYYY).", default="")
parser.add_argument('-s', "--skip", type=str, help="Skip a data type.", choices=["expenses", "income"], default="")
parser.add_argument('-i', "--ignored", help="Print ignored CSV data.", action="store_true")
args = parser.parse_args()

def main():
    # Get TD
    td = TDReader()
    td_withdrawls, td_deposits = td.get_data()

    # Get PC
    pc = PCReader()
    pc_withdrawls, pc_deposits = pc.get_data()

    withdrawls = td_withdrawls + pc_withdrawls
    deposits = td_deposits + pc_deposits

    sort(withdrawls)
    sort(deposits)

    withdrawls = filter_before_cutoff(withdrawls)
    deposits = filter_before_cutoff(deposits)

    if args.after != "":
        withdrawls, deposits = filter_after(args.after, withdrawls, deposits)

    if args.before != "":
        withdrawls, deposits = filter_before(args.before, withdrawls, deposits)

    withdrawls_c = Categorizer("withdrawls")
    deposits_c = Categorizer("deposits")

    withdrawls_c.remove_ignored(withdrawls, args.ignored)
    deposits_c.remove_ignored(deposits, args.ignored)
    print()

    if args.ignored:
        input("Press ENTER to continue...")

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
