import pandas as pd
from datetime import date,timedelta
import os

path = os.path.dirname(os.path.realpath(__file__))
# print(path)
df = pd.read_excel(path+"/Holidays.xlsx")
df['Dates'] = pd.to_datetime(df['Dates']).dt.date

# Check for whether it is holiday or not
def check_holiday(dat):
    if ((dat in df['Dates'].to_list()) or (dat.weekday() in [5,6])):
        return True
    else:
        return False
## Check for previous working day

def prev_working_day(dat):
    while(1):
        dat = dat-timedelta(1)
        if ((dat in df['Dates'].to_list()) or (dat.weekday() in [5,6])):
            continue
        else:
            return dat

check_holiday(date.today())

# print(prev_working_day(date.today()))


