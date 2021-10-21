import numpy as np
import pandas as pd 

class Backtest:
    def __init__(self, cash, data, signal, rebal_freq, ls=(70, 30)):
        self.ls = ls
        self.cash = float(cash)
        self.data = data
        self.signal = signal
        self.rebal_freq = rebal_freq

        self.symbols = list(self.data["close"].columns)
        self.timeline = list(self.data.index)
        self.position = self.construct_position_dataframe()
        self.holdings = self.construct_holdings_dataframe()
        self.account = self.construct_account_dataframe()
        # TODO: Add option for discrete shares

    def construct_position_dataframe(self):
        position = pd.DataFrame(np.nan, 
                        index=self.timeline, 
                        columns = self.symbols
                        )
        position.index.names = ["date"]
        return position

    def construct_holdings_dataframe(self):
        holdings = pd.DataFrame(np.nan, 
                        index=self.timeline, 
                        columns = self.symbols
                        )
        holdings.index.names = ["date"]
        return holdings


    def construct_account_dataframe(self):
        account = pd.DataFrame(0, index = self.timeline, columns = ["equities", "cash"])
        account.index.names = ["date"]
        return account

    def run(self):
        equity = self.cash
        counter = 0
        net_holdings = 0
        long_current_position = pd.Series(0, index = self.symbols)
        short_current_position = pd.Series(0, index = self.symbols)
        current_position = pd.Series(0.0, index=self.symbols)

        for t in self.timeline:
            if (counter == self.rebal_freq) or (counter == 0):
                # Update total equity
                if current_position.abs().sum() != 0:
                    # Update portfolio before changing position
                    equity = (current_position * self.data["close"].loc[t, self.symbols]).sum() + self.cash
                    current_position = self.data["stock splits"].loc[t, self.symbols] * current_position # Adjust for splits
                    current_position = current_position + (
                        (self.data["dividends"].loc[t, self.symbols] * current_position)/self.data["close"].loc[t, self.symbols]
                    ) # Reinvest dividends
                    long_current_position.loc[current_position > 0] = current_position.loc[current_position > 0]
                    short_current_position.loc[current_position < 0] = current_position.loc[current_position < 0]
                    net_holdings = (current_position * self.data["close"].loc[t, self.symbols]).sum() # Update net holdings value 

                # Update long positions w/ new signals
                long_signal = (self.signal.loc[t, self.symbols] == 1).astype(int)
                long_signal_count = (long_signal).abs().sum()
                if long_signal_count > 0:
                    # Update long positions 
                    long_alloc = (equity * self.ls[0]/100.0)/long_signal_count
                    long_current_position = long_alloc/(long_signal * self.data["close"].loc[t, self.symbols])
                    long_current_position.replace([np.inf, -np.inf], 0, inplace=True, regex=True)
                    long_current_position.fillna(0, inplace=True)
                else:
                    long_alloc = 0
                    long_current_position = long_alloc/(long_signal * self.data["close"].loc[t, self.symbols])
                    long_current_position.replace([np.inf, -np.inf], 0, inplace=True, regex=True)
                    long_current_position.fillna(0, inplace=True)

                short_signal = -(self.signal.loc[t, self.symbols] == -1).astype(int)
                short_signal_count = (short_signal).abs().sum()
                if short_signal_count > 0:
                    short_alloc = (equity * self.ls[1]/100.0)/short_signal_count
                    short_current_position = short_alloc/(short_signal * self.data["close"].loc[t, self.symbols])
                    short_current_position.replace([np.inf, -np.inf], 0, inplace=True, regex=True)
                    short_current_position.fillna(0, inplace=True)
                else:
                    short_alloc = 0
                    short_current_position = short_alloc/(short_signal * self.data["close"].loc[t, self.symbols])
                    short_current_position.replace([np.inf, -np.inf], 0, inplace=True, regex=True)
                    short_current_position.fillna(0, inplace=True)
                
                current_position = long_current_position + short_current_position
                # print(current_position)
                self.position.loc[t, self.symbols] = current_position # Assign to dataframe

                # Update holdings w/ new signals
                value = current_position * self.data["close"].loc[t, self.symbols]
                self.cash -= (value.sum() - net_holdings) 
                self.holdings.loc[t, self.symbols] = value

                # Update account w/ portfolio adjustments
                self.account.loc[t,"equities"] = value.sum() # Assign to dataframe
                self.account.loc[t,"cash"] = self.cash # Assign to dataframe
                
                counter = 1
            
            else:
                current_position = self.data["stock splits"].loc[t, self.symbols] * current_position # Adjust for splits
                current_position = current_position + (
                    (self.data["dividends"].loc[t, self.symbols] * current_position)/self.data["close"].loc[t, self.symbols]
                ) # Reinvest dividends
                long_current_position.loc[current_position > 0] = current_position.loc[current_position > 0]
                short_current_position.loc[current_position < 0] = current_position.loc[current_position < 0]
                
                # Update portfolio values
                net_holdings = (current_position * self.data["close"].loc[t, self.symbols]).sum()
                equity = net_holdings + self.cash
                self.position.loc[t, self.symbols] = current_position
                self.holdings.loc[t, self.symbols] = current_position * self.data["close"].loc[t, self.symbols]
                
                self.account.loc[t,"equities"] = net_holdings
                self.account.loc[t,"cash"] = self.cash
                
                counter += 1

        self.holdings = self.holdings.merge(self.account["cash"], on="date")
        return self.position, self.holdings, self.account