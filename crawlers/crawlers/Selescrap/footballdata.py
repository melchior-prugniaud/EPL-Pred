import pandas as pd
from selenium import webdriver
import random as rdn
import seaborn as sns
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import time
import os
import math
import statsmodels.api as sm
import statsmodels.formula.api as smf
from Final.functions import *
if not os.path.exists(os.getcwd()+"Data"):
    os.mkdir('Data')
    import urllib.request
    base = 'https://www.football-data.co.uk/'
    for i in range(0,10):
        season= str(10+i)+str(11+i)
        for j in ['E0','E1','E2','E3']:
            url =base+'mmz4281/'+season+'/'+ j +'.csv'
            chemin=os.getcwd()+"/Data/ENG_"+season+'_'+j+'.csv'
            urllib.request.urlretrieve(url,chemin)
            ResultatsSelectionVariable(chemin)
concat = pd.DataFrame()
for element in os.listdir('Data'):
    if element.startswith('ENG_'):
        ResultatsSelectionVariable('Data/'+element)
        df = pd.read_csv('Data/'+element)
        concat = pd.concat([concat,df])
concat.drop('Unnamed: 0',axis=1,inplace=True)
concat.to_csv('Data/Matchs_ENG.csv')
