import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
import time


stock_data = pd.read_csv('C:\\Users\\kim56\\anaconda3\\Find-A\\quant\\Fama_French\\factor_data.csv', index_col = 0, parse_dates=['날짜'], dtype = {'티커' : 'str'})

window = 252

tickers = stock_data['티커'].unique()
dt = pd.DataFrame(stock_data['날짜'].unique(), columns = ['날짜'])
abs_momentums = []

for i, ticker in enumerate(tickers) : 
    start = time.time()
    stock = stock_data[stock_data['티커'] == ticker]
    momentum = stock['등락률'].rolling(window = window, min_periods = 1).mean()
    abs_momentum = pd.DataFrame(stock['등락률'] - momentum)
    abs_momentum.rename(columns = {'등락률' : 'ABS_MOM'}, inplace = True)
    abs_momentum['티커'] = ticker
    stock = pd.concat([stock, abs_momentum], axis = 1)
    stock = pd.merge(stock, dt, how = 'outer', on = '날짜')
    abs_momentums.append(stock)
    end = time.time()
    print(f'[{i+1}/{len(tickers)}]({ticker}) was completed ... ({end - start:.5f} sec) ')
    
stock_data_mom = pd.concat(abs_momentums)
stock_data_mom.to_csv('./mom_data.csv')


