import os
import tempfile
from subprocess import call

def edit(data, new_indexes, data_type="withdrawls"):
    temp = tempfile.NamedTemporaryFile(prefix=f"{data_type}-", suffix=".tmp", mode="w+")

    new_data = []
    try:
        for i in new_indexes:
            to_csv = ",".join(data[i])
            temp.write(to_csv + "\n")
            temp.flush()

        call(["vim", temp.name])

        temp.seek(0)

        for row in temp.readlines():
            new_data.append(row.rstrip("\n").split(","))

    finally:
        temp.close()

    for i, i_value in enumerate(new_indexes):
        data[i_value] = new_data[i]
