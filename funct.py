import pandas as pd
import math
import numpy as np
from scipy.stats import poisson
import statsmodels.api as sm
import statsmodels.formula.api as smf
import os
from datetime import datetime

#Ensemble des fonctions utilisés
def ResultatsSelectionVariable(file_path):
    """
        Prends en entrée un chemin de fichier d'une saison et d'une compétition pour ne garder que les variables prédéterminer.
        Le descriptif des variables est disponible ici : https://www.football-data.co.uk/notes.txt
        Sauvegarde le fichier avec les colonnes.
    """
    season="20"+file_path[len(file_path)-11:-7][:2]+"/20"+file_path[len(file_path)-11:-7][2:]
    df = pd.read_csv(file_path)
    df= df.filter(['Div','Date','HomeTeam','AwayTeam','FTGH','FTHG','FTAG','FTR','B365H','B365D','B365A'])
    df['Season']=season
    df.to_csv(file_path)
def getDateTimeStamp(Date):
    """
    Transformation de la date en pd.Timestamp
    """
    dt =Date.split('/')
    return pd.Timestamp(int(dt[0]),int(dt[1]),int(dt[2]))
def NbButs(Date,saison,Eq,df):
    """
    Nb de buts d'une équipe jusqu'à une date donnée
    """
    date = getDateTimeStamp(Date)
    df = df[(df.Date <= date) & (df.Season == saison)]
    return df[df.HomeTeam == Eq].FTHG.sum() + df[df.AwayTeam == Eq].FTAG.sum(),df[df.HomeTeam == Eq].FTHG.sum(),df[df.AwayTeam == Eq].FTAG.sum()
def NbPts(Date,saison,league,equipe,df):
    """
    Nb de points à une date
    """
    d =Classement(Date,saison,league,df)
    return list(d[d.Eq == equipe].Pts)[0]
def Rate(Date,saison,df,team,rate):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    if rate == 'W':
        param = ['H','A']
    elif rate == 'D':
        param = ['D','D']
    else:
        param = ['A','H']
    df = df[((df.Season == saison )& (df.Date < date)) & ((df.HomeTeam == team)|(df.AwayTeam == team))]
    nb_match = len(df[df.HomeTeam == team])+len(df[df.AwayTeam == team])
    if nb_match == 0:
        return 0
    else:
        return (len(df[((df.HomeTeam == team) & (df.FTR ==param[0]))|(df.AwayTeam==team) & (df.FTR == param[1])])/nb_match)
def NbMatchJoue(Date,saison,df,team):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    df = df[((df.Season == saison )& (df.Date < date)) & ((df.HomeTeam == team)|(df.AwayTeam == team))]
    return len(df[df.HomeTeam == team])+len(df[df.AwayTeam == team])
def NbJoursRepos(Date,saison,df,team):
    """Ne prends pas malheureusement les matchs de coupe/LDC en compte"""
    import datetime
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    df = df[((df.Season == saison )& (df.Date < date)) & ((df.HomeTeam == team)|(df.AwayTeam == team))]
    dt = df.Date.max()
    if len(df)==0:
        return 60
    return (date - dt).days
def getNbGoal(Date,saison,df,team,place):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    if place == 'Dom':
        df = df[(df.Season == saison )& (df.Date < date) & (df.HomeTeam == team)]
        return df.FTHG.sum()
    elif place == 'Ext':
        df = df[(df.Season == saison )& (df.Date < date) & (df.AwayTeam == team)]
        return df.FTAG.sum()
def getNbGoalAgainst(Date,saison,df,team,place):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    if place == 'Dom':
        df = df[(df.Season == saison )& (df.Date < date) & (df.HomeTeam == team)]
        return df.FTAG.sum()
    elif place == 'Ext':
        df = df[(df.Season == saison )& (df.Date < date) & (df.AwayTeam == team)]
        return df.FTHG.sum()
def Classement(Date,saison,league,df):
    """
    Calcul du classement à une date
    """
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    df = df[(df.Date < date) & (df.Season == saison) & (df.Div == league)]
    eq = set(list(df.HomeTeam.unique())+list(df.AwayTeam.unique()))
    dic = { i : [0,0] for i in eq }
    for index,row in df.iterrows():
        if row.FTHG > row.FTAG:
            dic[row.HomeTeam][0]+=3
            dic[row.HomeTeam][1]+=row.FTHG
            dic[row.AwayTeam][0]+=1
            dic[row.AwayTeam][1]+=row.FTAG
        elif row.FTHG == row.FTAG:
            dic[row.HomeTeam][0]+=2
            dic[row.HomeTeam][1]+=row.FTHG
            dic[row.AwayTeam][0]+=2
            dic[row.AwayTeam][1]+=row.FTAG
        elif row.FTHG < row.FTAG:
            dic[row.HomeTeam][0]+=1
            dic[row.HomeTeam][1]+=row.FTHG
            dic[row.AwayTeam][0]+=3
            dic[row.AwayTeam][1]+=row.FTAG
    eq = list(dic.keys())
    Pts = [list(dic.values())[i][0] for i in range(len(list(dic.values())))]
    Buts = [list(dic.values())[i][1] for i in range(len(list(dic.values())))]
    return pd.DataFrame([eq,Pts,Buts],index=['Eq','Pts','Buts']).T.sort_values(['Pts','Buts'],ascending=False)
def GetCurrentClassement(Date,saison,df,team,league):
    clase= Classement(Date,saison,league,df)
    if len(clase)==0:
        return 0
    clase.index = range(len(clase))
    if not team in clase.Eq.unique():
        return 0
    else:
        return clase[clase.Eq == team].index[0]+1
def EtatDeForme(Date,saison,df,team,nb=5):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    df = df[((df.Season == saison) & (df.Date < date)) & ((df.HomeTeam == team)|(df.AwayTeam == team))].tail(nb)
    if len(df)==0:
        return 0
    else:
        nb_match = len(df)
        if df[(df.HomeTeam == team)].FTR.sum() == 0 and df[(df.AwayTeam == team)].FTR.sum() !=0:
            nbW = df[(df.AwayTeam == team)].FTR.sum().count('A')
        elif df[(df.HomeTeam == team)].FTR.sum() != 0 and df[(df.AwayTeam == team)].FTR.sum() ==0:
            nbW = df[(df.HomeTeam == team)].FTR.sum().count('H')
        elif df[(df.HomeTeam == team)].FTR.sum() == 0 and df[(df.AwayTeam == team)].FTR.sum() ==0:
            nbW=0
        else:
            nbW = df[(df.HomeTeam == team)].FTR.sum().count('H')+df[(df.AwayTeam == team)].FTR.sum().count('A')
        ptW = 3*nbW
        if df[(df.HomeTeam == team)].FTR.sum() == 0 and df[(df.AwayTeam == team)].FTR.sum() !=0:
            nbD = df[(df.AwayTeam == team)].FTR.sum().count('D')
        elif df[(df.HomeTeam == team)].FTR.sum() != 0 and df[(df.AwayTeam == team)].FTR.sum() ==0:
            nbD = df[(df.HomeTeam == team)].FTR.sum().count('D')
        elif df[(df.HomeTeam == team)].FTR.sum() == 0 and df[(df.AwayTeam == team)].FTR.sum() ==0:
            nbD = 0
        else:
            nbD=df[(df.HomeTeam == team)].FTR.sum().count('D')+df[(df.AwayTeam == team)].FTR.sum().count('D')
        ptD = 2*nbD
        if df[(df.HomeTeam == team)].FTR.sum() == 0 and df[(df.AwayTeam == team)].FTR.sum() !=0:
            ptL = df[(df.AwayTeam == team)].FTR.sum().count('H')
        elif df[(df.HomeTeam == team)].FTR.sum() != 0 and df[(df.AwayTeam == team)].FTR.sum() ==0:
            ptL = df[(df.HomeTeam == team)].FTR.sum().count('A')
        elif df[(df.HomeTeam == team)].FTR.sum() == 0 and df[(df.AwayTeam == team)].FTR.sum() ==0:
            ptL = 0
        else:
            ptL = df[(df.HomeTeam == team)].FTR.sum().count('A')+df[(df.AwayTeam == team)].FTR.sum().count('H')
        return (ptW+ptD+ptL)
def HFA(df,Date,saison,team):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    df = df[(df.Season == saison )& (df.Date < date) & (df.HomeTeam == team)]
    nb_matchs = len(df)
    if nb_matchs == 0:
        return 0
    return (df.FTHG.sum()-df.FTAG.sum())/nb_matchs
def Win_rate_against(df,Date,teamA,teamB,match_max=5):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    df = df[(df.Date < date)]
    df = df[((df.HomeTeam == teamA) & (df.AwayTeam == teamB)) | ((df.HomeTeam == teamB) & (df.AwayTeam == teamA))]
    if len(df) == 0:
        return 0
    nb_matchs = len(df)
    sub_df = df[(df.HomeTeam == teamA) & (df.AwayTeam == teamB)].FTR.sum()
    if not type(sub_df)==int:
        wh = sub_df.count('H')
    else:
        wh=0
    sub_df = df[(df.HomeTeam == teamB) & (df.AwayTeam == teamA)].FTR.sum()
    if not type(sub_df)==int:
        wa = sub_df.count('A')
    else:
        wa = 0
    return (wh+wa)/nb_matchs
def Undefeat_streak(df,Date,team):
    import warnings
    warnings.filterwarnings('ignore')
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    df_temp = df[((df.Date < date)) & ((df.HomeTeam == team) | (df.AwayTeam == team))]
    df_temp.sort_values('Date',ascending=False,inplace=True)
    cpt = 0
    for index,row in df_temp.iterrows():
        if (row.HomeTeam == team and row.FTR == 'H' or row.FTR == 'D') or (row.AwayTeam == team and row.FTR == 'A' or row.FTR == 'D'):
            cpt+=1
        else:
            return cpt
class Pi_rating:
    """
    Basé sur l'article : http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.719.6378&rep=rep1&type=pdf
    Propose un systeme de ranking basé sur l'avantage à domicile,l'impact du temps sur les résultats..
    """
    def __init__(self,equipes):
        """
            Ex : self.equipes['Arsenal']=['R_ArsenalH','R_Arsenal_Away','Overall']
        """
        self.equipes = {i : [0,0,0] for i in equipes}
        self.lmbda=0.0035
        self.yalta = 0.7
    def pi_rating_update(self,teamA,teamB,date,df):
        r_aH,r_aA = self.equipes[teamA][0],self.equipes[teamA][1]
        r_bH,r_bA = self.equipes[teamB][0],self.equipes[teamB][1]
        expected_gD= self.predicted_goal_diff(r_aH,r_bA)
        gD = self.real_goal_diff(teamA,teamB,date,df)
        error_H,error_A = self.error_update(expected_gD,gD)
        old_r_aH = self.equipes[teamA][0]
        old_r_bH = self.equipes[teamB][0]
        self.equipes[teamA][0]+=error_H*self.lmbda
        self.equipes[teamA][1]+=(self.equipes[teamA][0]-old_r_aH)*self.yalta
        self.equipes[teamB][0]+=error_A*self.lmbda
        self.equipes[teamB][1]+=(self.equipes[teamB][0]-old_r_bH)*self.yalta
        self.equipes[teamA][2]=(self.equipes[teamA][0]+self.equipes[teamA][1])/2
        self.equipes[teamB][2]=(self.equipes[teamB][0]+self.equipes[teamB][1])/2
        return [self.equipes[teamA][0],self.equipes[teamA][1],self.equipes[teamA][2]],[self.equipes[teamB][0],self.equipes[teamB][1],self.equipes[teamB][2]]
    def predicted_goal_diff(self,r_aH,r_bA):
        gDH = 10**(abs(r_aH)/3)-1
        gDA = 10**(abs(r_bA)/3)-1
        if r_aH < 0:
            gDH=-gDH
        if r_bA < 0:
            gDA=-gDA
        return gDH-gDA
    def real_goal_diff(self,teamA,teamB,Date,df):
        try:
            date = getDateTimeStamp(Date)
        except:
            date=Date
        scoreH = list(df[(df.HomeTeam == teamA) &  (df.Date == date)].FTHG)[0]
        scoreA = list(df[(df.AwayTeam == teamB) &  (df.Date == date)].FTAG)[0]
        return abs(scoreH-scoreA)
    def error_update(self,expected_gD,gD):
        error =  abs(gD-expected_gD)
        if expected_gD<gD:
            error_update_H = 3*math.log10(1+error)
            error_update_A = -3*math.log10(1+error)
        else:
            error_update_H = -3*math.log10(1+error)
            error_update_A = 3*math.log10(1+error)
        return error_update_H,error_update_A
def MaherxGt(df,Date,saison,HomeTeam,AwayTeam,div):
    try:
        date = getDateTimeStamp(Date)
    except:
        date=Date
    if saison == '2009/2010':
        return [0 for i in range(5)]
    if div != 'E0':
        return [0 for i in range(5)]
    else:
        nbmatchHT = len(df[((df.Season == saison )& (df.Date < date)) & ((df.HomeTeam == HomeTeam)|(df.AwayTeam == HomeTeam))])
        nbmatchAT = len(df[((df.Season == saison )& (df.Date < date)) & ((df.HomeTeam == AwayTeam)|(df.AwayTeam == AwayTeam))])
        if nbmatchHT > 19 and nbmatchAT > 19:
            df = df[(df.Date < date) & (df.Season == saison) & (df.Div == div)]
            data = pd.concat([df[['HomeTeam','AwayTeam','FTHG']].assign(home=1).rename(
                        columns={'HomeTeam':'team', 'AwayTeam':'opponent','FTHG':'buts'}),
                       df[['AwayTeam','HomeTeam','FTAG']].assign(home=0).rename(
                        columns={'AwayTeam':'team', 'HomeTeam':'opponent','FTAG':'buts'})])
            data.dropna(axis=0,inplace=True)
            poisson_model = smf.glm(formula="buts ~ home + team + opponent", data=data, 
                                    family=sm.families.Poisson()).fit()
            home_goals = poisson_model.predict(pd.DataFrame(data = {'team':HomeTeam,'opponent':AwayTeam,
                                                                   'home':1},index=[1])).values[0]
            away_goals = poisson_model.predict(pd.DataFrame(data = {'team':AwayTeam,'opponent':AwayTeam,
                                                                   'home':0},index=[1])).values[0]
            team_pred = [[poisson.pmf(i, team_avg) for i in range(0, 9)] for team_avg in [home_goals, away_goals]]
            sim = np.outer(np.array(team_pred[0]), np.array(team_pred[1]))
            predHWin = np.sum(np.tril(sim, -1))
            predDraw = np.sum(np.diag(sim))
            predAWin = np.sum(np.triu(sim, 1))
            return [home_goals,away_goals,predHWin,predDraw,predAWin]
        else:
            df2 = df[(df.Date < date) & (df.Season == saison)]
            home_goals = list(df2[df2['HomeTeam'] == HomeTeam][['FTHG']].sum().values)[0]
            away_goals = list(df2[df2['AwayTeam'] == AwayTeam][['FTAG']].sum().values)[0]
            if (home_goals == 0 or away_goals == 0) or (len(df2[df2['HomeTeam'] == HomeTeam])+len(df2[df2['AwayTeam'] == AwayTeam]) <4):
                last_saison = str(int(saison.split('/')[0])-1)+'/'+str(int(saison.split('/')[1])-1)
                df = df[(df.Date < pd.Timestamp(int(saison.split("/")[0]),7,31)) & (df.Season == last_saison)]
                home_goals = list(df[df['HomeTeam'] == HomeTeam][['FTHG']].mean().values)[0]
                away_goals = list(df[df['AwayTeam'] == AwayTeam][['FTAG']].mean().values)[0]
                p_home = df[df['HomeTeam']==HomeTeam][['FTHG']].apply(pd.value_counts,normalize=True)
                home_pmf = [poisson.pmf(i,np.sum(np.multiply(p_home.values.T,p_home.index.T),axis=1)[0]) for i in range(20)]
                p_away = df[df['AwayTeam']==AwayTeam][['FTAG']].apply(pd.value_counts,normalize=True)
                away_pmf = [poisson.pmf(i,np.sum(np.multiply(p_away.values.T,p_away.index.T),axis=1)[0]) for i in range(20)]
                sim = np.outer(np.array(home_pmf),np.array(away_pmf))
                predHWin = np.sum(np.tril(sim, -1))
                predDraw = np.sum(np.diag(sim))
                predAWin = np.sum(np.triu(sim, 1))
                return [home_goals,away_goals,predHWin,predDraw,predAWin]
            else:
                home_goals = list(df2[df2['HomeTeam'] == HomeTeam][['FTHG']].mean().values)[0]
                away_goals = list(df2[df2['AwayTeam'] == AwayTeam][['FTAG']].mean().values)[0]
                p_home = df2[df2['HomeTeam']==HomeTeam][['FTHG']].apply(pd.value_counts,normalize=True)
                home_pmf = [poisson.pmf(i,np.sum(np.multiply(p_home.values.T,p_home.index.T),axis=1)[0]) for i in range(20)]
                p_away = df2[df2['AwayTeam']==AwayTeam][['FTAG']].apply(pd.value_counts,normalize=True)
                away_pmf = [poisson.pmf(i,np.sum(np.multiply(p_away.values.T,p_away.index.T),axis=1)[0]) for i in range(20)]
                sim = np.outer(np.array(home_pmf),np.array(away_pmf))
                predHWin = np.sum(np.tril(sim, -1))
                predDraw = np.sum(np.diag(sim))
                predAWin = np.sum(np.triu(sim, 1))
                return [home_goals,away_goals,predHWin,predDraw,predAWin]
def season(x):
    return str(x)+"/"+str(x+1)
def deFinetti(model,X,y):
    pred = model.predict_proba(X)
    if len(pred) == len(y):
        deF=0
        for i in range(len(pred)):
            if y.iloc[i] == 1:
                a,b,c=1,0,0
            elif y.iloc[i] == 0:
                a,b,c=0,1,0
            else:
                a,b,c=0,0,1
            deF += (pred[i][2]-a)**2+(pred[i][1]-b)**2+(pred[i][0]-c)**2
    return deF/len(pred)
def transform_target(x):
    if x == 'H':
        return 1
    elif x == 'D':
        return 0
    elif x == 'A':
        return -1
def RankProbabilityScore(model,X,y):
    pred = model.predict_proba(X)
    RPS = 0
    for i in range(len(pred)):
        if y.iloc[i] == 1:
            a,b,c=1,0,0
        elif y.iloc[i] == 0:
            a,b,c=0,1,0
        else:
            a,b,c=0,0,1
        RPS += (pred[i][2]-a)**2+(pred[i][1]-b)**2+(pred[i][0]-c)**2
    return (RPS*0.5)/len(pred)
class Pi_ratingExist:
    """
    Basé sur l'article : http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.719.6378&rep=rep1&type=pdf
    Propose un systeme de ranking basé sur l'avantage à domicile,l'impact du temps sur les résultats..
    """
    def __init__(self,equipes):
        """
            Ex : self.equipes['Arsenal']=['R_ArsenalH','R_Arsenal_Away','Overall']
        """
        self.equipes = equipes
        self.lmbda=0.0035
        self.yalta = 0.7
    def pi_rating_update(self,teamA,teamB,date,df):
        r_aH,r_aA = self.equipes[teamA][0],self.equipes[teamA][1]
        r_bH,r_bA = self.equipes[teamB][0],self.equipes[teamB][1]
        expected_gD= self.predicted_goal_diff(r_aH,r_bA)
        gD = self.real_goal_diff(teamA,teamB,date,df)
        error_H,error_A = self.error_update(expected_gD,gD)
        old_r_aH = self.equipes[teamA][0]
        old_r_bH = self.equipes[teamB][0]
        self.equipes[teamA][0]+=error_H*self.lmbda
        self.equipes[teamA][1]+=(self.equipes[teamA][0]-old_r_aH)*self.yalta
        self.equipes[teamB][0]+=error_A*self.lmbda
        self.equipes[teamB][1]+=(self.equipes[teamB][0]-old_r_bH)*self.yalta
        self.equipes[teamA][2]=(self.equipes[teamA][0]+self.equipes[teamA][1])/2
        self.equipes[teamB][2]=(self.equipes[teamB][0]+self.equipes[teamB][1])/2
        return [self.equipes[teamA][0],self.equipes[teamA][1],self.equipes[teamA][2]],[self.equipes[teamB][0],self.equipes[teamB][1],self.equipes[teamB][2]]
    def predicted_goal_diff(self,r_aH,r_bA):
        gDH = 10**(abs(r_aH)/3)-1
        gDA = 10**(abs(r_bA)/3)-1
        if r_aH < 0:
            gDH=-gDH
        if r_bA < 0:
            gDA=-gDA
        return gDH-gDA
    def real_goal_diff(self,teamA,teamB,Date,df):
        try:
            date = getDateTimeStamp(Date)
        except:
            date=Date
        scoreH = list(df[(df.HomeTeam == teamA) &  (df.Date == date)].FTHG)[0]
        scoreA = list(df[(df.AwayTeam == teamB) &  (df.Date == date)].FTAG)[0]
        return abs(scoreH-scoreA)
    def error_update(self,expected_gD,gD):
        error =  abs(gD-expected_gD)
        if expected_gD<gD:
            error_update_H = 3*math.log10(1+error)
            error_update_A = -3*math.log10(1+error)
        else:
            error_update_H = -3*math.log10(1+error)
            error_update_A = 3*math.log10(1+error)
        return error_update_H,error_update_A
def getLastPiRatAll(fmatchs):
    equipes = {i : 0 for i in set(list(fmatchs[(fmatchs.Div== 'E0')].HomeTeam.unique())+list(fmatchs[(fmatchs.Div== 'E0')].HomeTeam.unique()))}
    for eq in equipes: 
        dt_H = fmatchs[fmatchs.HomeTeam == eq].Date.max()
        dt_A = fmatchs[fmatchs.AwayTeam == eq].Date.max()
        if dt_H > dt_A :
            choix = fmatchs[fmatchs.HomeTeam ==eq]
            choix = choix[choix.Date == dt_H]
            lp = [choix.PiRatHH.values[0],choix.PiRatHA.values[0],choix.PiRatHO.values[0]]
            equipes[eq] = lp
        else:
            choix = fmatchs[fmatchs.AwayTeam ==eq]
            choix = choix[choix.Date == dt_A]
            lp = [choix.PiRatAH.values[0],choix.PiRatAA.values[0],choix.PiRatAO.values[0]]
            equipes[eq] = lp
    return equipes
def getLastPiRat(fmatchs,eq):
    dt_H = fmatchs[fmatchs.HomeTeam == eq].Date.max()
    dt_A = fmatchs[fmatchs.AwayTeam == eq].Date.max()
    if dt_H > dt_A :
        choix = fmatchs[fmatchs.HomeTeam ==eq]
        choix = choix[choix.Date == dt_H]
        lp = [choix.PiRatHH.values[0],choix.PiRatHA.values[0],choix.PiRatHO.values[0]]
        return lp
    else:
        choix = fmatchs[fmatchs.AwayTeam ==eq]
        choix = choix[choix.Date == dt_A]
        lp = [choix.PiRatAH.values[0],choix.PiRatAA.values[0],choix.PiRatAO.values[0]]
        return lp
def getFullEloRank(club):
    import requests
    import pandas as pd
    page = requests.get('http://api.clubelo.com/'+club)
    L = page.text.split('\n')[1:]
    try :
        lst=[]
        for it in L:
            lst+=[(it.split(","))]
        return pd.DataFrame(lst,columns=page.text.split('\n')[0].split(','))
    except:
        print('Error on',club)
        return pd.DataFrame(columns=['Rank', 'Club', 'Country', 'Level', 'Elo', 'From', 'To'])
def getDfRank(df,verbose=False):
    import requests
    import pandas as pd
    equipes = set(list(df.HomeTeam.unique()) + list(df.AwayTeam.unique()))
    data = pd.DataFrame(columns=['Rank', 'Club', 'Country', 'Level', 'Elo', 'From', 'To'])
    for eq in equipes:
        if verbose ==True:
            print('============ PROCESSING {} ==================='.format(eq))
        if ' ' in eq:
            eq = eq.replace(' ','')
        temp = getFullEloRank(eq)
        data = pd.concat([data,temp])
    df['CleH'] = df.HomeTeam + '/'+ df.Date.map(str).apply(lambda x: x[0:10])
    df['CleA'] = df.AwayTeam + '/'+ df.Date.map(str).apply(lambda x: x[0:10])
    data['Cle'] = data.Club + '/'+data.To.map(str).apply(lambda x: x[0:10])
    subdata = data[['Cle','Elo']]
    test =pd.merge(df,subdata,how = 'left',left_on='CleH',right_on ='Cle')
    test.rename({'Elo':'EloH'},axis=1,inplace=True)
    test =pd.merge(test,subdata,how = 'left',left_on='CleA',right_on ='Cle')
    test.rename({'Elo':'EloA'},axis=1,inplace=True)
    test.drop(['CleH','CleA','Cle_x','Cle_y'],axis=1,inplace=True)
    return test
def probaPredictElo(rankA,rankB):
    pA = 1.0/(1.0+(10**((rankB-rankA)/400)))
    pB = 1.0/(1.0+(10**((rankA-rankB)/400)))
    return pA,pB
def addToLog(txt):
    from datetime import datetime
    print(txt)
    with open('Data/log.txt','a') as f:
        f.write(txt+ ' | '+str(datetime.now())+'\n')
def getLast(varH,varA,team,df):
    hd = df[df.HomeTeam == team].Date.max()
    ad = df[df.AwayTeam == team].Date.max()
    if hd > ad:
        d = hd
        lieu = df.HomeTeam
        c='Home'
    else:
        d= ad
        lieu = df.AwayTeam
        c='Away'
    sub = df[(df.Date == d) & (lieu == team)]
    if c == 'Home':
        return sub[varH].values[0]
    else:
        return sub[varA].values[0]
def TransfoCible(x):
    if x == 'H':
        return 1
    elif x=='A':
        return -1
    else:
        return 0
def diff(a,b):
    return a-b
def conseil(KC,phw,pd,paw,bk,ht,at):
    """
        Input : 
            KC = Kelly Criterion
            phw = Prob Home Win
            pd  = Prod Draw
            paw = Prob Away Win
            bk  = Cote bookmaker
            ht  = Home Team
            at  = Away Team
        Output : 
            Conseil sur quoi parier. 
    """
    if phw > pd and phw> paw:
        result = "l'équipe domicile"
        cote = 1/round(phw,2)
    elif pd> phw and pd> paw:
        result = 'le match nul'
        cote = 1/round(pd,2)
    elif paw > phw and paw> pd:
        result = "l'équipe extérieur"
        cote = 1/round(paw,2)
    if KC < 0 :
        return """La cote calculée par l'algorithme ({}) est plus élévée que celle du bookmaker ({}).\n
        Par conséquent, nous vous conseillons de ne pas parier même si le résultat semble être {}.""".format(round(cote,2),bk,result)
    else:
        if abs(phw-pd) < 0.05 or abs(paw-pd) < 0.05 or abs(phw-paw) < 0.05:
            return """La cote calculée par l'algorithme est intéressante ({}) comparée à celle du bookmaker ({}).\n
            Néanmoins il existe une trop légère différence entre les différents résultats prédits possibles.\n
            Par conséquent, même si nous vous recommandons de parier {}% de votre bankroll sur {} faites attention.
            """.format(round(cote,2),bk,round(KC,2),result)
        else:
            return """Nous vous conseillons de parier sur {} à hauteur de {}% de votre bankroll.\n
            La cote calculée étant de {} contre {} pour le bookmaker.
            """.format(result,round(KC,2),round(cote,2),bk)
def conclusion(hg,ag,choix):
    """
        Input : 
            hg : Home Goals
            ag : Away goal
            choix : résultat du choix de l'algo
        Output:
            Indicatrice : 1 si raison , 0 si faux
    """
    if not hg == 99:
        if hg > ag:
            result = 'H'
        elif ag == hg:
            result = 'D'
        else:
            result = 'A'
        if choix == result:
            return 1
        else:
            return 0
def Indice_confiance(pw,pd,pa):
    """
        Input : 
            pw : Prob Home Win
            pd : Prob Draw
            pa : Prob Away Win
        Output: 
            Indice de confiance sur le résultat du match de la forme x ( pour mettre sur le site avec des étoiles)
    """
    if pw > pd and pw > pa:
        choix = pw
    elif pd > pw and pd > pa:
        choix = pd
    elif pa > pw and pa > pd:
        choix = pa
    if choix > 0 and choix <0.3:
        return 1
    elif choix >= 0.3 and choix <0.5:
        return 2
    elif choix >= 0.5 and choix < 0.7:
        return 3
    elif choix >= 0.7 and choix <0.9:
        return 4
    else:
        return 5
def RankProbabilityScore(model,X,y):
    pred = model.predict_proba(X)
    RPS = 0
    for i in range(len(pred)):
        if y.iloc[i] == 1:
            a,b,c=1,0,0
        elif y.iloc[i] == 0:
            a,b,c=0,1,0
        else:
            a,b,c=0,0,1
        RPS += (pred[i][2]-a)**2+(pred[i][1]-b)**2+(pred[i][0]-c)**2
    return (RPS*0.5)/len(pred)