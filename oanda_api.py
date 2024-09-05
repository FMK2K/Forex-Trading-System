import requests
import pandas as pd
import defs
import utils

class OandaAPI:

    def __init__(self):
        self.session = requests.Session()

    def fetch_instruments(self):
        url = f"{defs.OANDA_URL}/accounts/{defs.ACCOUNT_ID}/instruments"
        response = self.session.get(url, params=None, headers=defs.SECURE_HEADER)
        return response.status_code, response.json()
    
    def get_instuments_df(self):
        code, data = self.fetch_instruments()
        if code == 200:
            df = pd.DataFrame.from_dict(data['instruments'])
            return df[['name', 'type', 'displayName', 'pipLocation', 'marginRate']]
        else:
            return None
        
    def save_instruments(self):
        df = self.get_instuments_df()
        if df is not None:
            df.to_pickle(utils.get_instruments_data_filename())

    def fetch_candles(self, pair_name, count=None, granularity="H1", date_from=None, date_to=None):
        url = f'{defs.OANDA_URL}/instruments/{pair_name}/candles'
        params = dict(
            granularity=granularity,
            price='MBA'
        )
        if date_from is not None and date_to is not None:
            params['to'] = int(date_to.timestamp())
            params['from'] = int(date_from.timestamp())
        elif count is not None:
            params['count'] = count
        else:
            params['count'] = 300

        response = self.session.get(url, params=params, headers=defs.SECURE_HEADER)
        #dealing with the lack of a response.json()
        if response.status_code != 200:
            return response.status_code, None
        
        return response.status_code, response.json()

if __name__ == '__main__':
    api = OandaAPI()

    # print(api.fetch_candles("EUR_NOK", 50, 'H4'))

    # print(api.fetch_instruments())

    # df = api.get_instuments_df()
    # print(df.head())
    
    # api.save_instruments()

    date_from = utils.get_utc_dt_from_string('2019-05-05 18:00:00')
    date_to = utils.get_utc_dt_from_string('2019-05-10 18:00:00')
    print(api.fetch_candles('EUR_CAD', date_from=date_from, date_to=date_to))

#THE FOLLOWING KEEPS GETTING RETURNED#
#    PS C:\Users\FeisalK\ForexBot> & c:/Users/FeisalK/ForexBot/Part4_Venv/venv/Scripts/python.exe c:/Users/FeisalK/ForexBot/Part4_Venv/oanda_api.py
#Traceback (most recent call last):
#  File "c:\Users\FeisalK\ForexBot\Part4_Venv\oanda_api.py", line 48, in <module>
#    date_from = utils.get_utc_dt_from_string('2019-05-05 18:00:00')  
#AttributeError: module 'utils' has no attribute 'get_utc_dt_from_string'

#Revise to ensure that get_utc_dt_from_string is correctly 
# defined and accessible in utils.py, and verify that there
#  are no naming conflicts or import errors. Check for
#  cached .pyc files and confirm that you are running the 
# script in the correct Python environment.