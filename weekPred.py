import pandas as pd
import math
from . import funct,addMatchs,checkNewEntries,ExtractionOddsWinamax
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import log_loss
from sklearn.metrics import accuracy_score

def addToLog(txt,quel):
    from datetime import datetime
    print(txt)
    with open('Data/log'+quel+'.txt','a') as f:
        f.write(txt+ ' | '+str(datetime.now())+'\n')
#Calcul des prédictions pour une journée
bankroll =100 # a definir
chemin_base = 'Data/Base.xlsx'
#récupérations des derniers résultats et ajouts
checkNewEntries.getNewEntries(chemin_base,chemin_last ='Data/ENG_1920_E0.csv')
addMatchs.addMatchs()

df = pd.read_excel('Data/Base.xlsx')
df = df[df.Div == 'E0']
df = df[df.Saison != 2009]

df['cible'] = df.FTR.apply(funct.TransfoCible)
df['diffRTHTRTAT']= df.apply(lambda row : funct.diff(row.RTHT,row.RTAT),axis=1)
df['diffTGHTTGAT']= df.apply(lambda row : funct.diff(row.TGHT,row.TGAT),axis=1)
df['diffEF']=df.apply(lambda row : funct.diff(row.EFH,row.EFA),axis=1)
df['diffStanding']=df.apply(lambda row : funct.diff(row.STHT,row.STAT),axis=1)

X = df[['SumValue_H','SumValue_A','WRH','WRA','diffEF','diffStanding','WRAH','WRAA','USHT','USAT',
        'PiRatHO','PiRatAO','MaherXG_HG','MaherXG_AG','EloHW','EloAW']]
y = df.cible

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBClassifier(seed=42)
model.fit(X_train,y_train)

addToLog("""=================TRAIN SET=============================Model1
DeFinetti : {}
RPS : {}
LogLoss : {}
Accuracy Score : {}\n
""".format(funct.deFinetti(model,X_train,y_train),funct.RankProbabilityScore(model,X_train,y_train),log_loss(y_train,model.predict_proba(X_train)),
          accuracy_score(y_train, model.predict(X_train))),'Metrics')
addToLog("""=================TEST SET=============================Model1
DeFinetti : {}
RPS : {}
LogLoss : {}
Accuracy Score : {}\n
""".format(funct.deFinetti(model,X_test,y_test),funct.RankProbabilityScore(model,X_test,y_test),log_loss(y_test,model.predict_proba(X_test)),
          accuracy_score(y_test, model.predict(X_test))),'Metrics')
nextm=ExtractionOddsWinamax.getNextOdds(30)
nextm['Season'] = '2019/2020'
nextm.replace('Sheffield Utd','Sheffield United',inplace=True)
nextm.replace('Manchester City','Man City',inplace=True)
nextm.replace('Manchester Utd','Man United',inplace=True)

#Ajout des variables pour la journée à venir
SumValue_H,SumValue_A,PiRatHO,PiRatAO,WRH,WRA=[],[],[],[],[],[]
MaherXG_HG,MaherXG_AG,WRAH,WRAA,USHT,USAT = [],[],[],[],[],[]
diffEF,diffStanding,EloA,EloH = [],[],[],[]
for index,row in nextm.iterrows():
    WRH.append(funct.Rate(row.Date,row.Season,df,row.HomeTeam,'W'))
    WRA.append(funct.Rate(row.Date,row.Season,df,row.AwayTeam,'W'))
    MaherXG_HG.append(funct.MaherxGt(df,row.Date,row.Season,row.HomeTeam,row.AwayTeam,"E0")[0])
    MaherXG_AG.append(funct.MaherxGt(df,row.Date,row.Season,row.HomeTeam,row.AwayTeam,"E0")[1])
    SumValue_H.append(funct.getLast('SumValue_H','SumValue_A',row.HomeTeam,df))
    SumValue_A.append(funct.getLast('SumValue_H','SumValue_A',row.AwayTeam,df))
    PiRatHO.append(funct.getLast('PiRatHO','PiRatAO',row.HomeTeam,df))
    PiRatAO.append(funct.getLast('PiRatHO','PiRatAO',row.AwayTeam,df))
    WRAH.append(funct.Win_rate_against(df,row.Date,row.HomeTeam,row.AwayTeam))
    WRAA.append(funct.Win_rate_against(df,row.Date,row.AwayTeam,row.HomeTeam))
    USHT.append(funct.Undefeat_streak(df,row.Date,row.HomeTeam))
    USAT.append(funct.Undefeat_streak(df,row.Date,row.AwayTeam))
    diffEF.append(funct.EtatDeForme(row.Date,row.Season,df,row.HomeTeam,nb=5)-funct.EtatDeForme(row.Date,row.Season,df,row.AwayTeam,nb=5))
    diffStanding.append(funct.GetCurrentClassement(row.Date,row.Season,df,row.HomeTeam,'E0')-funct.GetCurrentClassement(row.Date,row.Season,df,row.AwayTeam,'E0'))
    EloH.append(funct.getLast('EloH','EloA',row.HomeTeam,df))
    EloA.append(funct.getLast('EloH','EloA',row.AwayTeam,df))
nextm['SumValue_H'] = SumValue_H
nextm['SumValue_A'] = SumValue_A
nextm['PiRatHO'] = PiRatHO
nextm['PiRatAO'] = PiRatAO
nextm['WRH']=WRH
nextm['WRA']=WRA
nextm['MaherXG_HG']=MaherXG_HG
nextm['MaherXG_AG']=MaherXG_AG
nextm['WRAH']=WRAH
nextm['WRAA']=WRAA
nextm['USHT']=USHT
nextm['USAT']=USAT
nextm['diffEF']=diffEF
nextm['diffStanding']=diffStanding
nextm['EloH']=EloH
nextm['EloA']=EloA
nextm['EloHW'],nextm['EloAW']=zip(*nextm.apply(lambda row : funct.probaPredictElo(float(row.EloH),float(row.EloA)),axis=1))

X_avenir=nextm[['SumValue_H','SumValue_A','WRH','WRA','diffEF','diffStanding','WRAH','WRAA','USHT','USAT',
        'PiRatHO','PiRatAO','MaherXG_HG','MaherXG_AG','EloHW','EloAW']]

#Predictions
lst=[]
inputs = X_avenir
proba = model.predict_proba(X_avenir)
preds =model.predict(X_avenir)
verbose=False
for index,row in nextm.iterrows():
    subdf = df[((df.HomeTeam == row.HomeTeam)| (df.AwayTeam == row.HomeTeam)) & (df.Date<row.Date)].tail(5)
    fiveH = []
    for index2, row2 in subdf.iterrows():
        if (row2.FTR == 'H' and row.HomeTeam == row2.HomeTeam) or (row2.FTR == 'A' and row.HomeTeam == row2.AwayTeam):
            fiveH.append('V')
        elif row2.FTR == 'D':
            fiveH.append('D')
        else:
            fiveH.append('L')
    subdf = df[((df.HomeTeam == row.AwayTeam)| (df.AwayTeam == row.AwayTeam)) & (df.Date<row.Date)].tail(5)
    fiveA = []
    for index2, row2 in subdf.iterrows():
        if (row2.FTR == 'H' and row.AwayTeam == row2.HomeTeam) or (row2.FTR == 'A' and row.AwayTeam == row2.AwayTeam):
            fiveA.append('V')
        elif row2.FTR == 'D':
            fiveA.append('D')
        else:
            fiveA.append('L')
    if preds[index] == -1:
        cote = proba[index][0]
        choix = 'A'
    elif preds[index] == 0:
        cote = proba[index][1]
        choix = 'D'
    elif preds[index] == 1:
        cote = proba[index][2]
        choix = 'H'
    b = float(row['B365'+choix])-1
    p = cote
    q = 1-p
    kelly_criterion = (b*p-q)/b
    con = funct.conseil(kelly_criterion,proba[index][2],proba[index][1],proba[index][0],float(row['B365'+choix]),row.HomeTeam,row.AwayTeam)
    if kelly_criterion >0:
        print('{} vs {}\nResultat Prédit : {}'.format(row.HomeTeam,row.AwayTeam,preds[index]))
        print('{} % de bankroll à place\t {}€'.format(kelly_criterion*100,kelly_criterion*bankroll))
        print('{} % de chance de gagner calculé'.format(cote*100))
        print('{} cote BK'.format(b+1))
    else :
        if verbose ==True:
            print('{} vs {}\nResultat Prédit : {}\nPAS DE BET A PLACER'.format(row.HomeTeam,row.AwayTeam,preds[index]))
            print('{} % de chance de gagner calculé'.format(cote*100))
            print('{} cote BK'.format(b+1))
            print(kelly_criterion)
    lst+=[(pd.to_datetime(row.Date,dayfirst=True),row.HomeTeam,row.AwayTeam,proba[index][2],proba[index][1],proba[index][0],inputs.loc[index][12],inputs.loc[index][13],inputs.loc[index][14],inputs.loc[index][15],choix,b+1,1/cote,kelly_criterion*100,con,fiveH,fiveA)]
bets = pd.DataFrame(lst,columns=['Date',"HomeTeam","AwayTeam","PHW","PD","PAW","MaherHG","MaherAG",'EloHW','EloAW',"Choix","CoteBk","CoteCalc","KC",'Conseil','FiveH','FiveA'])
past_bets = pd.read_csv('Data/logPred2.csv',encoding='latin')
bets = pd.concat([past_bets,bets])
bets.to_csv('Data/logPred2.csv',index=False,encoding='latin1')