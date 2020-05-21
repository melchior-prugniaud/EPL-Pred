import pandas as pd
from . import funct
from datetime import datetime
#AJOUT DES DERNIERS MATCHS JOUES

# récupération de la base contenant les matchs précédents.
def addMatchs():
    fmatchs = pd.read_excel('Data/Base.xlsx')
    #match manquants
    df = pd.read_excel('Data/diff.xlsx')
    df = df.filter(['Div','Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','B365H','B365D','B365A','Season'])
    df.Date = pd.to_datetime(df.Date,dayfirst =True)
    #donnees de transfert_market
    tm = pd.read_csv('Data/BPL_transfert_market3.csv')
    #Ensemble de traitement du fichier
    tm.Valeur = tm.Valeur.apply(lambda x : int(x.replace('€','').replace('.00m','000000').replace('k','000').replace('-','0').replace('m','0000').replace('.',''))/1000000)
    tm['Age'] = tm.DateNaissance.replace('- (-)','').apply(lambda x: int(x[-3:-1]) if len(x)>1 else 0)
    tm['Taille'].fillna(180,inplace=True)
    tm['Taille'] = tm['Taille'].replace(' m','180')
    tm['Taille'] = tm.Taille.apply(lambda x:int(str(x).replace(',','').replace('m','')))
    tm.Taille=tm.Taille.apply(lambda x: str(x).replace("m",'').replace(",",""))
    tm.Taille.fillna(0,inplace=True)
    tm.Taille=tm.Taille.replace('nan',0)
    tm.Taille=tm.Taille.replace(' ',0)
    tm.Taille=tm.Taille.map(int)
    #jointure entre les deux tables
    dic2 = set(list(fmatchs[fmatchs.Div ==  'E0'].HomeTeam.unique())+list(fmatchs[fmatchs.Div ==  'E0'].AwayTeam.unique()))
    dic2 = {i for i in dic2 if pd.notna(i)}
    dic2= {sorted(dic2)[i] : i+1 for i in range(len(dic2))}
    df = pd.merge(df,pd.DataFrame(dic2.items(),columns=['Equipe','Cle_eq_H']),how='left',left_on='HomeTeam',right_on='Equipe')
    df.drop('Equipe',axis=1,inplace=True)
    df = pd.merge(df,pd.DataFrame(dic2.items(),columns=['Equipe','Cle_eq_A']),how='left',left_on='AwayTeam',right_on='Equipe')
    df.drop('Equipe',axis=1,inplace=True)
    dic = {i : 0 for i in sorted(list(tm.Equipe.unique()))}
    dic['AFC Bournemouth'],dic['Arsenal FC'],dic['Aston Villa'],dic['Birmingham City']=7,1,2,3
    dic['Blackburn Rovers'],dic['Blackpool FC'],dic['Bolton Wanderers']=4,5,6
    dic['Brighton & Hove Albion'],dic['Burnley FC'],dic['Cardiff City']=8,9,10
    dic['Chelsea FC'],dic['Crystal Palace'],dic['Everton FC']=11,12,13
    dic['Fulham FC'],dic['Huddersfield Town'],dic['Hull City']=14,15,16
    dic['Leicester City'],dic['Liverpool FC'],dic['Manchester City']=17,18,19
    dic['Manchester United'],dic['Middlesbrough FC'],dic['Newcastle United']=20,21,22
    dic['Norwich City'],dic['Queens Park Rangers'],dic['Reading FC']=23,25,26
    dic['Sheffield United'],dic['Southampton FC'],dic['Stoke City']=27,28,29
    dic['Sunderland AFC'],dic['Swansea City'],dic['Tottenham Hotspur']=30,31,32
    dic['Watford FC'],dic[ 'West Bromwich Albion'],dic['West Ham United']=33,34,35
    dic['Wigan Athletic'],dic['Wolverhampton Wanderers']=36,37
    tm=pd.merge(tm,pd.DataFrame(dic.items(),columns=['Equipe','cle_eq']),how='left',on='Equipe')
    lst=[]
    for eq in tm.Equipe.unique():
        for saison in tm.Saison.unique():
            cle_eq = tm[tm.Equipe == eq].cle_eq.values[0]
            valeurs = list(tm[(tm.Equipe == eq)& (tm.Saison == saison)][['Nationalité']].apply(pd.value_counts).head(2).values)
            avg = tm[(tm.Equipe == eq ) & (tm.Saison == saison)].Valeur.mean()
            somme = tm[(tm.Equipe == eq ) & (tm.Saison == saison)].Valeur.sum()
            taille = tm[(tm.Equipe == eq ) & (tm.Saison == saison)].Taille.mean()
            age = tm[(tm.Equipe == eq ) & (tm.Saison == saison)].Age.mean()
            if not valeurs == []:
                lst +=[(valeurs[0][0],valeurs[1][0],avg,somme,taille,age,saison,cle_eq)]
    data= pd.DataFrame(lst,columns=['MaxNbJMN_1_H','MaxNbJMN_2_H','AvgValue_H','SumValue_H','AvgH_H','AvgA_H','Saison_H','Cle_eq'])
    data2= pd.DataFrame(lst,columns=['MaxNbJMN_1_A','MaxNbJMN_2_A','AvgValue_A','SumValue_A','AvgH_A','AvgA_A','Saison_A','Cle_eq'])
    df['Saison'] = df.Season.apply(lambda x:x[:4])
    df['CleLiaisonH'] = df['Cle_eq_H'].fillna(99).map(int).map(str)+'_'+df['Saison'].map(str)
    data['CleLiaison']=data['Cle_eq'].map(str)+'_'+data['Saison_H'].map(str)
    df = pd.merge(df,data,how='left',left_on='CleLiaisonH',right_on='CleLiaison').drop(['Saison_H','Cle_eq','CleLiaison','CleLiaisonH'],axis=1)
    df['CleLiaisonA'] = df['Cle_eq_A'].fillna(99).map(int).map(str)+'_'+df['Saison'].map(str)
    data2['CleLiaison']=data2['Cle_eq'].map(str)+'_'+data2['Saison_A'].map(str)
    df =pd.merge(df,data2,how='left',left_on='CleLiaisonA',right_on='CleLiaison')
    df.drop(['Saison_A','Cle_eq','CleLiaison','CleLiaisonA'],axis=1,inplace=True)
    #Utilisation des fonctions crées
    df['WRH'] = df.apply(lambda row:funct.Rate(row['Date'],row['Season'],fmatchs,row['HomeTeam'],'W'),axis=1)
    df['WRA'] = df.apply(lambda row:funct.Rate(row['Date'],row['Season'],fmatchs,row['AwayTeam'],'W'),axis=1)
    df['DRH'] = df.apply(lambda row:funct.Rate(row['Date'],row['Season'],fmatchs,row['HomeTeam'],'D'),axis=1)
    df['DRA'] = df.apply(lambda row:funct.Rate(row['Date'],row['Season'],fmatchs,row['AwayTeam'],'D'),axis=1)
    df['LRH'] = df.apply(lambda row:funct.Rate(row['Date'],row['Season'],fmatchs,row['HomeTeam'],'L'),axis=1)
    df['LRA'] = df.apply(lambda row:funct.Rate(row['Date'],row['Season'],fmatchs,row['AwayTeam'],'L'),axis=1)
    df['PMHT'] = df.apply(lambda row:funct.NbMatchJoue(row["Date"],row['Season'],fmatchs,row['HomeTeam']),axis=1)
    df['PMAT'] = df.apply(lambda row:funct.NbMatchJoue(row["Date"],row['Season'],fmatchs,row['AwayTeam']),axis=1)
    df['RTHT'] = df.apply(lambda row:funct.NbJoursRepos(row["Date"],row['Season'],fmatchs,row['HomeTeam']),axis=1)
    df['RTAT'] = df.apply(lambda row:funct.NbJoursRepos(row["Date"],row['Season'],fmatchs,row['AwayTeam']),axis=1)
    df['TGHH'] = df.apply(lambda row:funct.getNbGoal(row["Date"],row['Season'],fmatchs,row['HomeTeam'],'Dom'),axis=1)
    df['TGHA'] = df.apply(lambda row:funct.getNbGoal(row["Date"],row['Season'],fmatchs,row['HomeTeam'],'Ext'),axis=1)
    df['TGHT'] = df['TGHH'] + df['TGHA'] 
    df['TGAH'] = df.apply(lambda row:funct.getNbGoal(row["Date"],row['Season'],fmatchs,row['AwayTeam'],'Dom'),axis=1)
    df['TGAA'] = df.apply(lambda row:funct.getNbGoal(row["Date"],row['Season'],fmatchs,row['AwayTeam'],'Ext'),axis=1)
    df['TGAT'] = df['TGAH'] + df['TGAA']
    df['TGAHH'] = df.apply(lambda row:funct.getNbGoalAgainst(row['Date'],row['Season'],fmatchs,row['HomeTeam'],'Dom'),axis=1)
    df['TGAHA'] = df.apply(lambda row:funct.getNbGoalAgainst(row['Date'],row['Season'],fmatchs,row['HomeTeam'],'Ext'),axis=1)
    df['TGAHT'] = df['TGAHH'] + fmatchs['TGAHA']
    df['TGAAH'] = df.apply(lambda row:funct.getNbGoalAgainst(row['Date'],row['Season'],fmatchs,row['AwayTeam'],'Dom'),axis=1)
    df['TGAAA'] = df.apply(lambda row:funct.getNbGoalAgainst(row['Date'],row['Season'],fmatchs,row['AwayTeam'],'Ext'),axis=1)
    df['TGAAT'] = df['TGAAH'] + df['TGAAA']
    df['HTGD'] = df['TGHT'] - df['TGAHT']
    df['ATGD'] = df['TGAT'] - df['TGAAT']
    df['HFA']= df.apply(lambda row : funct.HFA(fmatchs,row['Date'],row['Season'],row['HomeTeam']),axis=1)
    df['EFH'] = df.apply(lambda row:funct.EtatDeForme(row['Date'],row['Season'],fmatchs,row['HomeTeam']),axis=1)
    df['EFA'] = df.apply(lambda row:funct.EtatDeForme(row['Date'],row['Season'],fmatchs,row['AwayTeam']),axis=1)
    df['STHT']=df.apply(lambda row:funct.GetCurrentClassement(row['Date'],row["Season"],fmatchs,row["HomeTeam"],row['Div']),axis=1)
    df['STAT']=df.apply(lambda row:funct.GetCurrentClassement(row['Date'],row["Season"],fmatchs,row["AwayTeam"],row['Div']),axis=1)
    df['WRAH']= df.apply(lambda row: funct.Win_rate_against(fmatchs,row['Date'],row['HomeTeam'],row['AwayTeam']),axis=1)
    df['WRAA']= df.apply(lambda row: funct.Win_rate_against(fmatchs,row['Date'],row['AwayTeam'],row['HomeTeam']),axis=1)
    df['USHT']= df.apply(lambda row : funct.Undefeat_streak(fmatchs,row['Date'],row['HomeTeam']),axis=1)
    df.USHT.fillna(0,inplace=True)
    df['USAT']= df.apply(lambda row : funct.Undefeat_streak(fmatchs,row['Date'],row['AwayTeam']),axis=1)
    df.USAT.fillna(0,inplace=True)
    PiRat = funct.Pi_ratingExist(funct.getLastPiRatAll(fmatchs))
    df['PiRatHH'],df['PiRatHA'],df['PiRatHO']=0.0,0.0,0.0
    df['PiRatAH'],df['PiRatAA'],df['PiRatAO']=0.0,0.0,0.0
    cpt=0
    for index,row in df.iterrows():
        f=PiRat.pi_rating_update(row.HomeTeam,row.AwayTeam,row.Date,df)
        df.loc[index,'PiRatHH'],df.loc[index,'PiRatHA'],df.loc[index,'PiRatHO']=f[0][0],f[0][1],f[0][2]
        df.loc[index,'PiRatAH'],df.loc[index,'PiRatAA'],df.loc[index,'PiRatAO']=f[1][0],f[1][1],f[1][2]
        cpt+=1
    df['MaherXG_HG'],df['MaherXG_AG'],df['MaherXG_PredHW'],df['MaherXG_PredD'],df['MaherXG_PredAW']=zip(*df.apply(lambda row:funct.MaherxGt(fmatchs,row['Date'],row['Season'],row['HomeTeam'],row['AwayTeam'],row['Div']),axis=1))

    df = funct.getDfRank(df)
    df['EloHW'],df['EloAW']=zip(*df.apply(lambda row : funct.probaPredictElo(float(row.EloH),float(row.EloA)),axis=1))
    matchs = pd.concat([fmatchs[df.columns],df])
    matchs.to_excel('Data/Base.xlsx')
    matchs.to_excel('Data/Base'+str(datetime.now().day)+'_'+str(datetime.now().month)+'.xlsx')
    funct.addToLog('{} nouvelles entrées ajoutées'.format(len(df)))