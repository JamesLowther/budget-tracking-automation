import argparse

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
    c.categorize(deposits, entry_type="deposits")
    c.categorize(withdrawls, entry_type="withdrawls")

    withdrawls, deposits = edit(withdrawls, deposits)

    print(deposits)

if __name__ == "__main__":
    main()
