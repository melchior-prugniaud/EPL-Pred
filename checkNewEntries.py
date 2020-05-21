import pandas as pd
import requests
import os
from datetime import datetime
import os
import urllib.request
#Obtention des matchs manquant de la derniere journée , dataframe diff
def addToLog(txt):
    print(txt)
    with open('Data/log.txt','a') as f:
        f.write(txt+ ' | '+str(datetime.now()))
def ResultatsSelectionVariable(file_path):
    """
        Prends en entrée un chemin de fichier d'une saison et d'une compétition pour ne garder que les variables prédéterminer.
        Le descriptif des variables est disponible ici : https://www.football-data.co.uk/notes.txt
        Sauvegarde le fichier avec les colonnes.
    """
    season="20"+file_path[len(file_path)-11:-7][:2]+"/20"+file_path[len(file_path)-11:-7][2:]
    df = pd.read_csv(file_path)
    df= df.filter(['Div','Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','B365H','B365D','B365A'])
    df['Season']=season
    df.to_csv(file_path)
def downloadMatchs():
    if not os.path.exists(os.getcwd()+"/Data"):
        os.mkdir('Data')
    base = 'https://www.football-data.co.uk/'
    for i in range(0,10):
        season= str(10+i)+str(11+i)
        for j in ['E0','E1','E2','E3']:
            url =base+'mmz4281/'+season+'/'+ j +'.csv'
            chemin=os.getcwd()+"/Data/ENG_"+season+'_'+j+'.csv'
            urllib.request.urlretrieve(url,chemin)
            ResultatsSelectionVariable(chemin)
def getNewEntries(chemin_base,chemin_last ='Data/ENG_1920_E0.csv'):
    downloadMatchs()
    base = pd.read_excel(chemin_base)
    last = pd.read_csv(chemin_last)
    last.Date = pd.to_datetime(last.Date,dayfirst =True)
    base['Cle']=base.Date.map(str)+'/'+base.HomeTeam+"/"+base.AwayTeam
    last['Cle'] = last.Date.map(str)+'/'+last.HomeTeam+"/"+last.AwayTeam
    diff = last.merge(base[['Cle']],how='outer',on='Cle',indicator=True).loc[lambda x : x['_merge']=='left_only']
    diff.to_excel('Data/diff.xlsx')
    addToLog('{} nouvelles entrées détectés'.format(len(diff)))