from pykrx import stock

import pandas as pd
import numpy as np

from pytimekr import pytimekr
import datetime
from datetime import timedelta

import time

import warnings
warnings.filterwarnings('ignore')

# 날짜 index 생성을 위한 함수 정의
def get_str_date_range(start, end, freq = 'BM'): # BM : 주말이 아닌 평일 중 각 달의 가장 마지막 날
    dr = list(pd.date_range(start, end, freq = freq))
    for i in range(len(dr)):
        date = dr[i].date()
        # 거래소가 개장하지 않는 경우에는 그 전날, 혹은 그 전전날의 주가 데이터를 가져옴.
        # ex. 공휴일, 주말, 경우에 따라 12월 30일이나 31일
        while (date in pytimekr.holidays(year=date.year)) or (date.weekday() >= 5) or (date.month == 12 and date.day >= 30) : 
            date = date - timedelta(days = 1)
        dr[i] = date.strftime("%Y%m%d")
    return dr

def get_filtered_info(start, end) : 
    date_range = get_str_date_range(start, end) 
    filtered_dict = {}
    results = []
    print('Start from', date_range[0])
    for i in range(len(date_range)) : 
        date = date_range[i]
        
        if i% 12 == 0 : 
            year = int(date_range[i][:4])
            june_data = stock.get_market_cap(date_range[i+5]).reset_index().sort_values(by = '시가총액')
            lower_bound = int(len(june_data) * 0.95)
            adjusted_june_data = june_data.iloc[:lower_bound, :][june_data['종가'] >= 5000]
            
            target_tickers = adjusted_june_data['티커'].unique()
            target_names = [stock.get_market_ticker_name(ticker) for ticker in target_tickers]
            filtered_dict[year] = pd.DataFrame({'티커' : target_tickers, '종목명' : target_names}).sort_values(by='종목명').reset_index(drop = True)
            
    return filtered_dict

def get_stock_data(start, end) : 
    date_range = get_str_date_range(start, end)
    filtered_info = get_filtered_info(start, end)
    results = []
    
    print('Start to get data from KRX ... ')
    
    
    for j, (year, info) in enumerate(filtered_info.items()) : 
        print(f'Downloading Data in {year}')
        filtered_tickers = info['티커'].to_numpy()
        filtered_names = info['종목명'].to_numpy()

        results_annual = []
        start_date = date_range[12*j]
        end_date = date_range[11+12*j]
        if j == 0 : 
            start_date = start
        for i, ticker in enumerate(filtered_tickers) : 

#                 try : 
            strt_t = time.time()
            print(f'[{i+1}/{len(filtered_tickers)}] Downloading {filtered_names[i]}({ticker}) data ...')
            stock_price = stock.get_market_ohlcv(start_date, end_date, ticker, adjusted = True).reset_index()
            stock_price['티커'] = ticker
            stock_price['종목명'] = filtered_names[i]

            time.sleep(0.5)

            market_cap = stock.get_market_cap(start_date, end_date, ticker).reset_index()[['날짜', '시가총액']]
            market_cap['티커'] = ticker

            result = pd.merge(stock_price, market_cap, on = ['티커', '날짜'])
            results_annual.append(result)

#                 except : 
#                     print(f'(skip) Downloading {filtered_names[i]}({ticker}), error occured. ')
#                     continue

            time.sleep(1)
            end_t = time.time()
            print(f'[{filtered_names[i]}({ticker})]{end_t-strt_t : .3f} sec')
        df_annual = pd.concat(results_annual).reset_index(drop = True)
        results.append(df_annual)
    df = pd.concat(results).reset_index(drop = True)[['티커', '종목명', '날짜', '종가', '거래량', '등락률', '시가총액']].sort_values(by=['종목명', '날짜']).reset_index(drop = True) 
            
    return df.drop_duplicates()
            


start = '20030101'
end = '20230101'
stock_df = get_stock_data(start, end)
stock_df