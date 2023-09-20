import FinanceDataReader as fdr

from pykrx import stock

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pytimekr import pytimekr
import datetime
from datetime import timedelta

import time
import pickle

stock_data = pd.read_pickle('C:/Users/kim56/anaconda3/Find-A/quant/Data/kospi200_data.p')

dt = np.sort(stock_data['날짜'].unique())

stock_data['Z_MOM'] = 0
stock_data['Z_PER'] = 0

for date in dt : 
    temp_mom = stock_data.loc[stock_data['날짜'] == date]['ABS_MOM']
    temp_per = stock_data.loc[stock_data['날짜'] == date]['PER']
    stock_data.loc[stock_data['날짜'] == date, 'Z_MOM'] = (temp_mom - temp_mom.mean()) / temp_mom.std()
    stock_data.loc[stock_data['날짜'] == date, 'Z_PER'] = (temp_per - temp_per.mean()) / temp_per.std()
print(stock_data)
stock_data.to_pickle('C:/Users/kim56/anaconda3/Find-A/quant/Data/kospi200_z_data.p')
