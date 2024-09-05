import os

import pandas as pd
import datetime as dt

from instrument import Instrument
import utils
from oanda_api import OandaAPI

INCREMENTS = {
    'M5' : 5, #5 min
    'H1' : 60, #1 hour
    'H4' : 240 #4 hour
}

def get_candles_df(json_response):
    prices = ['mid','bid','ask']
    ohlc = ['o','h','l','c']
    
    our_data = []
    for candle in json_response['candles']:
        if candle['complete'] == False:
            continue

        new_dict = {}
        new_dict['time'] = candle['time']
        new_dict['volume'] = candle['volume']
        for price in prices:
            for oh in ohlc:
                new_dict[f"{price}_{oh}"] = candle[price][oh]
        our_data.append(new_dict)
    return pd.DataFrame.from_dict(our_data)

def create_file(pair, granularity, api):
    candle_count = 2000
    time_step = INCREMENTS[granularity] * candle_count

    end_date = utils.get_utc_dt_from_string("2024-08-03 23:59:59")
    date_from = utils.get_utc_dt_from_string("2019-01-01 00:00:00")

    candle_dfs = []

    date_to = date_from
    while date_to < end_date:
        date_to = date_from + dt.timedelta(minutes=time_step)
        if date_to > end_date:
            date_to = end_date
        #print(date_from, date_to)
        code, json_data = api.fetch_candles(pair,
                                            granularity = granularity,
                                            date_from = date_from,
                                            date_to = date_to)
        if code == 200 and len(json_data['candles'])>0:
            candle_dfs.append(get_candles_df(json_data))
        elif code != 200:
            print('ERROR', pair, granularity, date_from, date_to,)
            break

        # collect candles ^
        date_from = date_to
    final_df = pd.concat(candle_dfs)
    final_df.drop_duplicates(subset='time', inplace=True)
    final_df.sort_values(by='time', inplace=True)

    final_df.to_pickle(utils.get_his_data_filename(pair, granularity))
    print(f"{pair} {granularity} {final_df.iloc[0].time}")
    #save dataframe^

def run_collection():
    pair_list = 'GBP,EUR,USD,CAD,JPY,NZD,CHF'
    api = OandaAPI()
    for g in INCREMENTS.keys():
        for i in Instrument.get_pairs_from_string(pair_list):
            filename = f"{i}_{g}"
            print(g, i)
            create_file(i, g, api)
            
            print("file "+filename+" created")

def updated_run_collection():
    pair_list = 'GBP,EUR,USD,CAD,JPY,NZD,CHF'
    api = OandaAPI()
    data_directory = "C:/Users/FeisalK/ForexBot/Part4_Venv/his_data"
    
    for g in INCREMENTS.keys():
        for i in Instrument.get_pairs_from_string(pair_list):
            filename = f"{i}_{g}"
            filepath = os.path.join(data_directory, filename)
            print(g, i)
            if os.path.exists(filepath):
                print(f"File {filename} already exists")
            else:
                create_file(i, g, api)
                print(f"File {filename} created")

if __name__ == "__main__":
    updated_run_collection()