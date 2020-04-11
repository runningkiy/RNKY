# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 17:36:54 2020

@author: 家琦
"""

import pandas as pd
import numpy as np

def m2q(month): #set the 1st,2nd,3rd,and 4th quarters by the month
    if month == 1 or month == 12 or month == 11:
        quarter = 4
    if month == 4 or month == 3 or month == 2:
        quarter = 1
    if month == 7 or month == 6 or month == 5:
        quarter = 2
    if month == 10 or month == 9 or month == 8:
        quarter = 3
            
    return(quarter)
    
def high_low(value, median): #Dividend the data to two part:low and high
    if value >= median:
        return('high')
    if value < median:
        return('low')

            # 'data_centers','diversified','health_care','industrial',
          #'infrastructure','industrial','infrastructure','mortgage',
          #'office','residential','retail','self_storage','timber','specialty'       
for r in ['data_centers','diversified','health_care','industrial',
          'infrastructure','mortgage','office','residential',
          'retail','self_storage','timber','specialty']:


    universe=pd.read_csv('uni_cleaned.csv') #REITs name and categories
    retail=universe[universe[r]==1] #choose diversified data
    resi=retail['symbol']         #Tickers
    px=pd.read_csv('reit_px.csv') #FFO data
    retail_px=px[px['ticker'].isin(resi)] #select retail FFO data
    df = pd.read_excel('fs_data_u.xlsx') #macro drivers data
    retail_px.head()
    
    cpi_col = ['year', 'qtr', 'infl', 'ann_inf']
    df_cpi = pd.DataFrame(columns = cpi_col) #build datafrmae of inflation and date
    
    gdp_col = ['year', 'qtr', 'gdp']
    df_gdp = pd.DataFrame(columns = gdp_col) #build dataframe of GDP and date
    
    spx_col = ['year', 'qtr', 'spx']
    df_spx = pd.DataFrame(columns = spx_col) #build dataframe of SP50
    
    ur_col = ['year', 'qtr', 'ur']
    df_ur = pd.DataFrame(columns = ur_col) #build dataframe of Unemployment rate
    
    hvr_col = ['year', 'qtr', 'hvr']
    df_hvr = pd.DataFrame(columns = hvr_col) #build dataframe of Unemployment rate
    
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
    
    df_ur['year'] = df['QtrEnd'].dt.year
    df_ur['qtr'] = df['QtrEnd'].dt.month.apply(m2q)
    df_ur['ur'] = df['Unemployment Rate']
    
    df_hvr['year'] = df['QtrEnd'].dt.year
    df_hvr['qtr'] = df['QtrEnd'].dt.month.apply(m2q)
    df_hvr['hvr'] = df['Home Vacancy Rate'] 
    
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
    
    ##Test2
    df_all = \
        (
        df_gdp
            .merge(df_cpi, on = ['year', 'qtr'])
            .merge(df_ur, on = ['year', 'qtr'])
            .merge(df_hvr, on = ['year', 'qtr'])
            .merge(df_spx, on = ['year', 'qtr'])
            .merge(retail_px, on = ['year', 'qtr'])
            .assign(spx_real = df_spx['spx']*4 - df_cpi['ann_inf'])
            #assign(heal_real = heal_px['heal_ret']/100-df_cpi['annual_inflation'])
        )
        
    inflation_median = df_all['ann_inf'].median()
    gdp_median = df_all['gdp'].median()
    ur_median = df_all['ur'].median()
    hvr_median = df_all['hvr'].median()
    df_all['return_real']=df_all['return']*4-df_all['ann_inf']
    df_all=df_all[['year','qtr','gdp','ann_inf','ur','hvr','spx_real','return_real']]
    df_all.head()
    ###
    '''
    print(r)
    
    
    print("High GDP, High Unemployment")
    print((df_all.query('gdp >= @gdp_median').query('ur >= @ur_median'))[['spx_real', 'return_real']].mean())
    print("High GDP, Low Unemployment")
    print((df_all.query('gdp >= @gdp_median').query('ur < @ur_median'))[['spx_real', 'return_real']].mean())
    print("Low GDP, High Unemployment")
    print((df_all.query('gdp < @gdp_median').query('ur >= @ur_median'))[['spx_real', 'return_real']].mean())
    print("Low GDP, Low Unemployment")
    print((df_all.query('gdp < @gdp_median').query('ur < @ur_median'))[['spx_real', 'return_real']].mean())
    print('\n')
    
    print("High inflation, High Housing Vacancy Rate")
    print((df_all.query('ann_inf >= @inflation_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].mean())

    '''
    print(r)
    
    
    print("High Unemployment Rate, High Housing Vacancy Rate")
    '''
    print((df_all.query('ur >= @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].mean())
    print("Standard Deviation")
    print((df_all.query('ur >= @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].std())
    '''
    print("Sharpe Ratio")
    print((df_all.query('ur >= @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].mean()\
          /(df_all.query('ur >= @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].std())
    
    print("High Unemployment Rate, Low Housing Vacancy Rate")
    '''
    print((df_all.query('ur >= @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].mean())
    print("Standard Deviation")
    print((df_all.query('ur >= @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].std())
    '''
    print("Sharpe Ratio")
    print((df_all.query('ur >= @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].mean()\
          /(df_all.query('ur >= @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].std())

    print("Low Unemployment Rate, High Housing Vacancy Rate")
    '''
    print((df_all.query('ur < @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].mean())
    print("Standard Deviation")
    print((df_all.query('ur < @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].std())
    '''
    print("Sharpe Ratio")
    print((df_all.query('ur < @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].mean()\
          /(df_all.query('ur < @ur_median').query('hvr >= @hvr_median'))[['spx_real', 'return_real']].std())

    print("Low Unemployment Rate, Low Housing Vacancy Rate")
    '''
    print((df_all.query('ur < @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].mean())
    print("Standard Deviation")
    print((df_all.query('ur < @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].std())
    '''
    print("Sharpe Ratio")
    print((df_all.query('ur < @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].mean()\
          /(df_all.query('ur < @ur_median').query('hvr < @hvr_median'))[['spx_real', 'return_real']].std())
    print('\n')
    