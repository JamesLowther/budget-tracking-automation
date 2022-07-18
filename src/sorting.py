
from datetime import datetime

def sort(data):
    data.sort(key=lambda x: (datetime.strptime(x[0], "%m-%d-%Y"), x[1], float(x[2])))
