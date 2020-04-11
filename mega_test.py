# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 19:44:52 2020

@author: 家琦
"""
from pandas import Series,DataFrame
import pandas as pd


namecol = {'data_centers':0,'diversified':0,'health_care':0,'industrial':0,
          'infrastructure':0,'mortgage':0,'office':0,'residential':0,
          'retail':0,'self_storage':0,'timber':0,'specialty':0}
regimelist = ['High Unemployment Rate, High Rental Vacancy Rate',
           'High Unemployment Rate, Low Rental Vacancy Rate',
           'Low Unemployment Rate, High Rental Vacancy Rate',
           'Low Unemployment Rate, Low Rental Vacancy Rate']

dicdata = {regimelist[0]:namecol,
           regimelist[1]:namecol,
           regimelist[2]:namecol,
           regimelist[3]:namecol}
dfmega = DataFrame(dicdata)

#megawriter=pd.ExcelWriter('megatest.xlsx')
























