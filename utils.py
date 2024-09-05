import datetime as dt
from dateutil.parser import *
import os

# SIMPLE FXN DEFINITIONS
def get_his_data_filename(pair, granularity):
    # Construct the full path to the file
    directory = os.path.join("C:/Users/FeisalK/ForexBot/Part4_Venv/his_data")
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create the directory if it doesn't exist
    
    filename = f"{pair}_{granularity}.pkl"
    filepath = os.path.join(directory, filename)

    # Check if the file already exists
    if os.path.isfile(filepath):
        return filepath
    else:
        # Just return the path to allow file creation later
        return filepath

#def get_instruments_data_filename():
#    return 'instruments.pkl'
def get_instruments_data_filename():
    # Return the absolute path to the instruments.pkl file
    return 'C:/Users/FeisalK/ForexBot/Part4_Venv/instruments.pkl'

def time_utc():
    return dt.datetime.now().replace(tzinfo=dt.timezone.utc)

def get_utc_dt_from_string(date_str):
    d = parse(date_str)
    return d.replace(tzinfo=dt.timezone.utc)

# the following is for the tester
if __name__ == '__main__':
     #print(get_his_data_filename("EUR_USD", "H1"))
    #print(get_instruments_data_filename())

    #print(dt.datetime.now(dt.timezone.utc))
    print(time_utc())
    print(get_utc_dt_from_string('2019-05-05 18:00:00'))


