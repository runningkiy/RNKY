# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 19:04:46 2020

@author: Arthur
"""

import pandas as pd

import numpy as np

universe=pd.read_csv('uni_cleaned.csv') #REITs name and categories
retail=universe[universe['diversified']==1] #choose diversified data
resi=retail['symbol']         #Tickers
px=pd.read_csv('reit_px.csv') #FFO data
retail_px=px[px['ticker'].isin(resi)] #select retail FFO data
df = pd.read_excel('fs_data.xlsx') #macro drivers data
retail_px.head()

cpi_col = ['year', 'qtr', 'infl', 'ann_inf']
df_cpi = pd.DataFrame(columns = cpi_col) #build datafrmae of inflation and date

gdp_col = ['year', 'qtr', 'gdp']
df_gdp = pd.DataFrame(columns = gdp_col) #build dataframe of GDP and date

spx_col = ['year', 'qtr', 'spx']
df_spx = pd.DataFrame(columns = spx_col) #build dataframe of SP50

def m2q(month): #set the 1st,2nd,3rd,and 4th quarters by the month
    if month == 1:
        quarter = 4
    if month == 4:
        quarter = 1
    if month == 7:
        quarter = 2
    if month == 10:
        quarter = 3
    if month == 3:
        quarter = 1
    if month == 6:
        quarter = 2
    if month == 9:
        quarter = 3
    if month == 12:
        quarter = 4
    if month == 2:
        quarter = 1
    if month == 5:
        quarter = 2
    if month == 8:
        quarter = 3
    if month == 11:
        quarter = 4
        
    return(quarter)
    
def high_low(value, median): #Dividend the data to two part:low and high
    if value >= median:
        return('high')
    if value < median:
        return('low')

df_cpi['year'] = df['QtrEnd'].dt.year
df_cpi['qtr'] = df['QtrEnd'].dt.month.apply(m2q)
df_cpi['infl'] = df['CPI']
df_cpi['ann_inf'] = df_cpi['infl'] * 4

df_gdp['year'] = df['QtrEnd'].dt.year
df_gdp['qtr'] = df['QtrEnd'].dt.month.apply(m2q)
df_gdp['gdp'] = df['GDP']

df_spx['year'] = df['QtrEnd'].dt.year
df_spx['qtr'] = df['QtrEnd'].dt.month.apply(m2q)
df_spx['spx'] = df['SP Real'] 


retail_px.date = pd.to_datetime(retail_px.date)
retail_px = retail_px.pivot_table(values='close',
                                  index='date',
                                  columns='ticker')
retail_px = retail_px.resample('Q',convention='end').last()
retail_px.reset_index(level=0,inplace=True)

start_date = '1999-12-31'
end_date = '2019-12-31'

mask = (retail_px['date'] >= start_date) & (retail_px['date'] <= end_date)

retail_px = retail_px.loc[mask]

'''Here, I have the quarterly close of several REITS. We equal-weight it by
taking the average of the columns.'''

ret = retail_px.mean(axis=1)
retail_px['return']=ret.pct_change()
retail_px = retail_px[1:]
#
retail_px['date'] = pd.to_datetime(retail_px['date'])
retail_px.assign(year = lambda df: df.date.dt.year)
temp = pd.DatetimeIndex(retail_px['date'])
retail_px['year'] = temp.year
retail_px['month'] = temp.month
retail_px['qtr']=retail_px['month'].apply(m2q)
retail_px=retail_px[['year', 'qtr','return']]
#
df_all = \
    (
    df_gdp
        .merge(df_cpi, on = ['year', 'qtr'])
        .merge(df_spx, on = ['year', 'qtr'])
        .merge(retail_px, on = ['year', 'qtr'])
        .assign(spx_real = df_spx['spx']*4 - df_cpi['ann_inf'])
        #assign(heal_real = heal_px['heal_ret']/100-df_cpi['annual_inflation'])
    )
    
inflation_median = df_all['ann_inf'].median()
gdp_median = df_all['gdp'].median()
df_all['return_real']=df_all['return']*4-df_all['ann_inf']
df_all=df_all[['year','qtr','gdp','ann_inf','spx_real','return_real']]
df_all.head()
print("diversified")
print("High GDP, High Infl")
print((df_all.query('gdp >= @gdp_median').query('ann_inf >= @inflation_median'))[['spx_real', 'return_real']].mean())
print("High GDP, Low Infl")
print((df_all.query('gdp >= @gdp_median').query('ann_inf < @inflation_median'))[['spx_real', 'return_real']].mean())
print("Low GDP, High Infl")
print((df_all.query('gdp < @gdp_median').query('ann_inf >= @inflation_median'))[['spx_real', 'return_real']].mean())
print("Low GDP, Low Infl")
print((df_all.query('gdp < @gdp_median').query('ann_inf < @inflation_median'))[['spx_real', 'return_real']].mean())