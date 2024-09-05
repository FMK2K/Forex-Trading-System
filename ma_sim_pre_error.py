import pandas as pd
from dateutil.parser import *

import utils
import instrument
import ma_result

#Moving avergage cross strategy
def is_trade(row):
    if row.DIFF >= 0 and row.DIFF_PREV < 0:
        return 1    #BUY
    if row.DIFF <= 0 and row.DIFF_PREV > 0:
        return -1   #SELL
    return 0    #NTHN

def get_ma_col(ma):
    return f'MA_{ma}'

def evaluate_pair(i_pair, mashort, malong, price_data):

    #Taking a subset of price_data --> for later duration of trade
    price_data = price_data[['time', 'mid_c', get_ma_col(mashort), get_ma_col(malong)]].copy()

    price_data['DIFF'] = price_data[get_ma_col(mashort)] - price_data[get_ma_col(malong)]
    price_data['DIFF_PREV'] = price_data.DIFF.shift(1)
    price_data['IS_TRADE'] = price_data.apply(is_trade, axis=1)
    
    df_trades = price_data[price_data.IS_TRADE!=0].copy()
    df_trades["DELTA"] = (df_trades.mid_c.diff() / i_pair.pipLocation).shift(-1)
    df_trades["GAIN"] = df_trades["DELTA"] * df_trades["IS_TRADE"]

    df_trades["PAIR"] = i_pair.name
    df_trades["MASHORT"] = mashort
    df_trades["MALONG"] = malong

    del df_trades[get_ma_col(mashort)]
    del df_trades[get_ma_col(malong)]

    df_trades['time'] = [parse(x) for x in df_trades.time]
    df_trades['DURATION'] = df_trades.time.diff().shift(-1)
    df_trades['DURATION'] = [x.total_seconds()/3600 for x in df_trades.DURATION]
    df_trades.dropna(inplace=True)

    #print(f"{i_pair.name} {mashort} {malong} trades:{df_trades.shape[0]} gain:{df_trades['GAIN'].sum():.0f}")

    return ma_result.MAResult(
        df_trades=df_trades,
        pairname=i_pair.name,
        params={'mashort' : mashort, 'malong' : malong}
    )

def get_price_data(pairname, granularity):
    df = pd.read_pickle(utils.get_his_data_filename(pairname, granularity))
    
    non_cols = ['time', 'volume']
    mod_cols = [x for x in df.columns if x not in non_cols]
    df[mod_cols] = df[mod_cols].apply(pd.to_numeric)

    return df[['time', 'mid_c']]

def process_data(short_ma, long_ma, price_data):
    ma_list = set(short_ma+long_ma)

    for ma in ma_list:
        price_data[get_ma_col(ma)] = price_data.mid_c.rolling(window=ma).mean()

    return price_data

def store_trades(results):
    all_trade_df_list = [x.df_trades for x in results]
    all_trade_df = pd.concat(all_trade_df_list)
    all_trade_df.to_pickle("all_trades.pkl")

def process_results(results):
    results_list = [r.result_ob() for r in results]
    final_df = pd.DataFrame.from_dict(results_list)

    final_df.to_pickle("ma_test_res.pkl")
    '''print(final_df.info())
    print(final_df.head())'''
    print(final_df.shape, final_df.num_trades.sum())

def get_test_pairs(pair_str):
    exhisting_pairs = instrument.Instrument.get_instruments_dict().keys()
    pairs = pair_str.split(",")

    test_list = []
    for p1 in pairs:
        for p2 in pairs:
            p = f"{p1}_{p2}"
            if p in exhisting_pairs:
                test_list.append(p)
    #print (test_list)            
    return test_list


def run():
    currencies = "GBP,EUR,CAD,JPY,NZD,CHF" #['EUR_CAD','...]
    granularity = 'H1'
    ma_short = [8 , 16, 32, 64]
    ma_long = [32, 64, 96, 128, 256]

    test_pairs = get_test_pairs(currencies)

    ''''Moved inside our loop to occur on each of our currency pairs'''
    #i_pair = instrument.Instrument.get_instruments_dict()[pairname]
    #price_data = get_price_data(pairname, granularity)
    #price_data=process_data(ma_short,ma_long,price_data)

    #print(price_data.tail())

    #SIMULATION VARIABLES --> replaced with a list
    #best = -1000000000.0 #best game
    #b_mashort = 0
    #b_malong = 0
    results=[]

    for pairname in test_pairs: 
        print(f'running pairname: {pairname}')
        i_pair = instrument.Instrument.get_instruments_dict()[pairname]
        
        price_data = get_price_data(pairname, granularity)
        price_data=process_data(ma_short,ma_long,price_data)

        for _malong in ma_long:
            for _mashort in ma_short:
                if _mashort >= _malong:
                    continue
                ###EVALUATE
                res = evaluate_pair(i_pair, _mashort, _malong, price_data.copy())
                '''if res > best:
                    best = res
                    b_mashort = _mashort
                    b_malong = _malong'''
                results.append(evaluate_pair(i_pair, _mashort, _malong, price_data))

    #print(f"Best:{best:.0f} MASHORT:{b_mashort:.0f} MALONG:{b_malong:.0f}")
    process_results(results)
    store_trades(results)
            


if __name__ == '__main__':
    #get_test_pairs('GBP,EUR,CAD,JPY,NZD,CHF')
    run()