import os
import tempfile
from subprocess import call

def edit(withdrawls, deposits):
    new_withdrawls = edit_list(withdrawls, entry_type="withdrawls")
    new_deposits = edit_list(deposits, entry_type="deposits")

    return (new_withdrawls, new_deposits)

def edit_list(data, entry_type="withdrawls"):
    temp = tempfile.NamedTemporaryFile(prefix=f"{entry_type}-", suffix=".tmp", mode="w+")

    new_data = []
    try:
        for row in data:
            to_csv = ",".join(row)
            temp.write(to_csv + "\n")
            temp.flush()

        call(["vim", temp.name])

        temp.seek(0)

        for row in temp.readlines():
            new_data.append(row.rstrip("\n").split(","))

    finally:
        temp.close()

    return new_data
