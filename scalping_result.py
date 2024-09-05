class ScalpingResult:
    # Class to structure the results of our RSI strategy simulation
    def __init__(self, df_trades, pairname, params):
        self.pairname = pairname  # Name of the currency pair
        self.df_trades = df_trades  # DataFrame containing trade information
        self.params = params  # Parameters used in the RSI strategy (e.g., RSI period)

    def result_ob(self):
        """
        Create a dictionary containing summary statistics and parameters of the RSI strategy simulation.
        """
        # Dictionary to store the summary statistics and parameters
        d = {
            'pair': self.pairname,
            'num_trades': self.df_trades.shape[0],
            'total_gain': self.df_trades.GAIN.sum(),
            'mean_gain': self.df_trades.GAIN.mean(),
            'min_gain': self.df_trades.GAIN.min(),
            'max_gain': self.df_trades.GAIN.max(),
            'mean_duration': self.df_trades.DURATION.mean(),
            'max_duration': self.df_trades.DURATION.max(),
            'min_duration': self.df_trades.DURATION.min()
        }

        # Add RSI period to the dictionary
        for k, v in self.params.items():
            d[k] = v

        return d
