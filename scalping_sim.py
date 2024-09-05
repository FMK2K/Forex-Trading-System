import pandas as pd
from dateutil.parser import parse
import utils
import instrument
import scalping_result

# Relative Strength Index (RSI) strategy
def is_trade(row, rsi_col):
    """
    Determine if a trade should be made based on RSI value.
    If RSI < 30, it's a BUY signal.
    If RSI > 70, it's a SELL signal.
    Otherwise, no trade.
    """
    if row[rsi_col] < 30:
        return 1  # BUY
    if row[rsi_col] > 70:
        return -1  # SELL
    return 0  # NTHN

def get_rsi_col(period):
    """
    Generate the column name for RSI based on the given period.
    """
    return f'RSI_{period}'

def calculate_rsi(price_data, period):
    """
    Calculate the RSI for a given period.
    RSI is calculated using average gains and losses over the specified period.
    """
    delta = price_data['mid_c'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def evaluate_pair(i_pair, rsi_period, price_data):
    """
    Evaluate the trading strategy for a specific currency pair and RSI period.
    """
    # Calculate RSI and add it to price_data
    rsi_col = get_rsi_col(rsi_period)
    price_data[rsi_col] = calculate_rsi(price_data, rsi_period)
    
    # Take a subset of price_data for the duration of the trade
    price_data = price_data[['time', 'mid_c', rsi_col]].copy()
    price_data['IS_TRADE'] = price_data.apply(lambda row: is_trade(row, rsi_col), axis=1)

    # Identify trades
    df_trades = price_data[price_data.IS_TRADE != 0].copy()
    df_trades["DELTA"] = (df_trades.mid_c.diff() / i_pair.pipLocation).shift(-1)
    df_trades["GAIN"] = df_trades["DELTA"] * df_trades["IS_TRADE"]

    # Add metadata to trades
    df_trades["PAIR"] = i_pair.name
    df_trades["RSI_PERIOD"] = rsi_period

    # Clean up columns
    del df_trades[rsi_col]

    # Parse time and calculate trade duration
    df_trades['time'] = [parse(x) for x in df_trades.time]
    df_trades['DURATION'] = df_trades.time.diff().shift(-1)
    df_trades['DURATION'] = [x.total_seconds()/3600 for x in df_trades.DURATION]
    df_trades.dropna(inplace=True)

    return scalping_result.ScalpingResult(
        df_trades=df_trades,
        pairname=i_pair.name,
        params={'rsi_period': rsi_period}
    )

def get_price_data(pairname, granularity):
    """
    Retrieve historical price data for a specified currency pair and granularity.
    """
    df = pd.read_pickle(utils.get_his_data_filename(pairname, granularity))

    # Ensure non-numeric columns are not converted
    non_cols = ['time', 'volume']
    mod_cols = [x for x in df.columns if x not in non_cols]
    df[mod_cols] = df[mod_cols].apply(pd.to_numeric)

    return df[['time', 'mid_c']]

def process_data(rsi_periods, price_data):
    """
    Calculate the RSI for all specified periods and add them to the price data.
    """
    for period in rsi_periods:
        price_data[get_rsi_col(period)] = calculate_rsi(price_data, period)
    return price_data

def store_trades(results):
    """
    Store the trades generated during the simulation to a pickle file for further analysis.
    """
    all_trade_df_list = [x.df_trades for x in results]
    all_trade_df = pd.concat(all_trade_df_list)
    all_trade_df.to_pickle("all_trades_rsi.pkl")

def process_results(results):
    """
    Process the simulation results and store them in a DataFrame, providing an overall summary of the trading performance.
    """
    results_list = [r.result_ob() for r in results]
    final_df = pd.DataFrame.from_dict(results_list)

    final_df.to_pickle("scal_test_res.pkl")
    print(final_df.shape, final_df.num_trades.sum())

def get_test_pairs(pair_str):
    """
    Generate a list of currency pairs to test based on a string of currency codes (e.g., "GBP,EUR,CAD,JPY,NZD,CHF").
    """
    existing_pairs = instrument.Instrument.get_instruments_dict().keys()
    pairs = pair_str.split(",")

    test_list = []
    for p1 in pairs:
        for p2 in pairs:
            p = f"{p1}_{p2}"
            if p in existing_pairs:
                test_list.append(p)
    return test_list

def run():
    """
    Main function that orchestrates the simulation.
    Iterates through each currency pair and RSI period, evaluates the strategy, and stores the results for analysis.
    """
    currencies = "GBP,EUR,CAD,JPY,NZD,CHF"  # Currencies to test
    granularity = 'H1'  # Data granularity (e.g., hourly data)
    rsi_periods = [14, 21, 28]  # RSI periods to test

    test_pairs = get_test_pairs(currencies)
    results = []

    for pairname in test_pairs: 
        print(f'running pairname: {pairname}')
        i_pair = instrument.Instrument.get_instruments_dict()[pairname]
        
        price_data = get_price_data(pairname, granularity)
        price_data = process_data(rsi_periods, price_data)

        for rsi_period in rsi_periods:
            res = evaluate_pair(i_pair, rsi_period, price_data.copy())
            results.append(res)

    process_results(results)
    store_trades(results)

if __name__ == '__main__':
    run()




