from datetime import datetime
import re

def remove_before(element, after):
    return datetime.strptime(element[0], "%m-%d-%Y") > datetime.strptime(after, "%m-%d-%Y")

def remove_after(element, before):
    return datetime.strptime(element[0], "%m-%d-%Y") < datetime.strptime(before, "%m-%d-%Y")

def filter_before(before, withdrawls, deposits):
    if bool(re.search("^\d{2}-\d{2}-\d{4}$", before)):
        withdrawls = list(filter(lambda x: remove_after(x, before), withdrawls))
        deposits = list(filter(lambda x: remove_after(x, before), deposits))
    else:
        print("after argument not in form MM-DD-YYYY. Ignoring.")

    return (withdrawls, deposits)

def filter_after(after, withdrawls, deposits):
    if bool(re.search("^\d{2}-\d{2}-\d{4}$", after)):
        withdrawls = list(filter(lambda x: remove_before(x, after), withdrawls))
        deposits = list(filter(lambda x: remove_before(x, after), deposits))
    else:
        print("before argument not in form MM-DD-YYYY. Ignoring.")

    return (withdrawls, deposits)
