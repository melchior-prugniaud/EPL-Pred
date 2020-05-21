from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import random as rdn
import time
from selenium.webdriver.support.ui import WebDriverWait


### Scraper pour extraire les compisitions de ScoreBoard.com
## Données non incluses dans le modèle pour le moment
lst=[]
lst_error = []
driver = webdriver.Chrome('chromedriver.exe')
def getComp(url):
    driver = webdriver.Chrome('chromedriver.exe')
    driver.get(url)
    element = driver.find_element_by_id('a-match-lineups')
    try:
        element.click()
    except:
        time.sleep(4)
        element.click()
    time.sleep(4)
    soup= BeautifulSoup(driver.page_source,'lxml')
    #### HomeTeamPlayers Start
    HomeTeamStarter = []
    for tr in soup.find('table',class_='parts').find_all('tr')[1:12]:
        if tr.find('td',class_='summary-vertical fl').find('div',class_='time-box'):
            numero = tr.find('td',class_='summary-vertical fl').find('div',class_='time-box').text
        else:
            numero = ''
        if tr.find('td',class_='summary-vertical fl').find('div',class_='name'):
            Joueur = tr.find('td',class_='summary-vertical fl').find('div',class_='name').text
        else:
            Joueur = ''
        if tr.find('td',class_='summary-vertical fl').find('span',class_='flag'):
            nationalite = tr.find('td',class_='summary-vertical fl').find('span',class_='flag')['title']
        else:
            nationalite = ''
        if tr.find('td',class_='summary-vertical fl').find('div',class_='name').find('a'):
            lien = tr.find('td',class_='summary-vertical fl').find('div',class_='name').find('a')['onclick'].replace("window.open('","https://www.scoreboard.com").replace("'); return false;",'')
            joueur_slug = lien.split('/')[5]
        else:
            lien = ''
            joueur_slug = ''
        HomeTeamStarter+= [(numero,Joueur,joueur_slug,nationalite,lien)]
    #### AwayTeamPlayers Start
    AwayTeamStarter = []
    for tr in soup.find('table',class_='parts').find_all('tr')[1:12]:
        if tr.find('td',class_='summary-vertical fr').find('div',class_='time-box'):
            numero = tr.find('td',class_='summary-vertical fr').find('div',class_='time-box').text
        else:
            numero = ''
        if tr.find('td',class_='summary-vertical fr').find('div',class_='name'):
            Joueur = tr.find('td',class_='summary-vertical fr').find('div',class_='name').text
        else:
            Joueur = ''
        if tr.find('td',class_='summary-vertical fr').find('span',class_='flag'):
            nationalite = tr.find('td',class_='summary-vertical fr').find('span',class_='flag')['title']
        else:
            nationalite = ''
        if tr.find('td',class_='summary-vertical fr').find('div',class_='name').find('a'):
            lien = tr.find('td',class_='summary-vertical fr').find('div',class_='name').find('a')['onclick'].replace("window.open('","https://www.scoreboard.com").replace("'); return false;",'')
            joueur_slug = lien.split('/')[5]
        else:
            lien = ''
            joueur_slug = ''
        AwayTeamStarter+= [(numero,Joueur,joueur_slug,nationalite,lien)]
    #### HomeTeamPlayers Sub
    HomeTeamSub = []
    for tr in soup.find('table',class_='parts').find_all('tr')[13:]:
        if tr.find('td',class_='summary-vertical fl').find('div',class_='time-box'):
            numero = tr.find('td',class_='summary-vertical fl').find('div',class_='time-box').text
        else:
            numero = ''
        if tr.find('td',class_='summary-vertical fl').find('div',class_='name'):
            Joueur = tr.find('td',class_='summary-vertical fl').find('div',class_='name').text
        else:
            Joueur = ''
        if tr.find('td',class_='summary-vertical fl').find('span',class_='flag'):
            nationalite = tr.find('td',class_='summary-vertical fl').find('span',class_='flag')['title']
        else:
            nationalite = ''
        if tr.find('td',class_='summary-vertical fl').find('div',class_='name').find('a'):
            lien = tr.find('td',class_='summary-vertical fl').find('div',class_='name').find('a')['onclick'].replace("window.open('","https://www.scoreboard.com").replace("'); return false;",'')
            joueur_slug = lien.split('/')[5]
        else:
            lien = ''
            joueur_slug = ''
        HomeTeamSub+= [(numero,Joueur,joueur_slug,nationalite,lien)]
    #### AwayTeamPlayers Sub
    AwayTeamSub = []
    for tr in soup.find('table',class_='parts').find_all('tr')[13:]:
        if tr.find('td',class_='summary-vertical fr').find('div',class_='time-box'):
            numero = tr.find('td',class_='summary-vertical fr').find('div',class_='time-box').text
        else:
            numero = ''
        if tr.find('td',class_='summary-vertical fr').find('div',class_='name'):
            Joueur = tr.find('td',class_='summary-vertical fr').find('div',class_='name').text
        else:
            Joueur = ''
        if tr.find('td',class_='summary-vertical fr').find('span',class_='flag'):
            nationalite = tr.find('td',class_='summary-vertical fr').find('span',class_='flag')['title']
        else:
            nationalite = ''
        if tr.find('td',class_='summary-vertical fr').find('div',class_='name').find('a'):
            lien = tr.find('td',class_='summary-vertical fr').find('div',class_='name').find('a')['onclick'].replace("window.open('","https://www.scoreboard.com").replace("'); return false;",'')
            joueur_slug = lien.split('/')[5]
        else:
            lien = ''
            joueur_slug = ''
        AwayTeamSub+= [(numero,Joueur,joueur_slug,nationalite,lien)]
    driver.quit()
    return HomeTeamStarter,AwayTeamStarter,HomeTeamSub,AwayTeamSub

for i in range(0,10):
    driver.get('https://www.scoreboard.com/en/soccer/england/premier-league-'+str(2010+i)+'-'+str(2010+i+1)+'/results/')
    SCROLL_PAUSE_TIME = 0.5
    # Get scroll height
    time.sleep(1)
    element  =driver.find_element_by_class_name('event__more--static')
    while True:
        try:
            element  =driver.find_element_by_class_name('event__more--static')
        except:
            break
        try:
            element.click()
            driver.execute_script("arguments[0].scrollIntoView();", element)
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(3)
        except:
            try:
                element  =driver.find_element_by_class_name('event__more--static')
                driver.execute_script("arguments[0].scrollIntoView();", element)
                element.click()
            except:
                break
        time.sleep(2)
    soup = BeautifulSoup(driver.page_source,'lxml')
    saison1 = 2010+i
    saison2 = 2010+i+1
    for match in soup.find_all('div',class_='event__match--oneLine'):
        if int(match.find('div',class_='event__time').text.replace('.','-').split(' ')[0].split('-')[1])>6:
            saison = saison1
        else:
            saison = saison2
        jour = match.find('div',class_='event__time').text.replace('.','-').split(' ')[0]+str(saison)
        heure = match.find('div',class_='event__time').text.replace('.','-').split(' ')[1]
        HomeTeam = match.find('div',class_='event__participant--home').text
        AwayTeam = match.find('div',class_='event__participant--away').text
        id_ = match['id'].split('_')[-1]
        url = 'https://www.scoreboard.com/en/match/'+id_ +'/#match-summary'
        try:
            titulaireHome,titulaireAway,remplaçantHome,remplaçantAway = getComp(url)
        except:
            titulaireHome,titulaireAway,remplaçantHome,remplaçantAway = [],[],[],[]
            lst_error.append(url)
        lst+=[(jour,heure,HomeTeam,AwayTeam,[j[0] for j in titulaireHome],[j[1] for j in titulaireHome],
               [j[2] for j in titulaireHome],[j[3] for j in titulaireHome],[j[4] for j in titulaireHome],
              [j[0] for j in titulaireAway],[j[1] for j in titulaireAway],
               [j[2] for j in titulaireAway],[j[3] for j in titulaireAway],[j[4] for j in titulaireAway],
             [j[0] for j in remplaçantHome],[j[1] for j in remplaçantHome],
               [j[2] for j in remplaçantHome],[j[3] for j in remplaçantHome],[j[4] for j in remplaçantHome],
             [j[0] for j in remplaçantAway],[j[1] for j in remplaçantAway],
               [j[2] for j in remplaçantAway],[j[3] for j in remplaçantAway],[j[4] for j in remplaçantAway])]
driver.quit()

df = pd.read_excel('Data/Base.xlsx')
data = pd.DataFrame(lst,columns=['Date','Heure','HomeTeam','AwayTeam','HomeTeamStartNum','HomeTeamStartName',
                                'HomeTeamStartSlug','HomeTeamStartNationalite','HomeTeamStartLien',
                                 'AwayTeamStartNum','AwayTeamStartName','AwayTeamStartSlug','AwayTeamStartNationalite',
                                 'AwayTeamStartLien','HomeTeamSubNum','HomeTeamSubName',
                                'HomeTeamSubSlug','HomeTeamSubNationalite','HomeTeamSubLien','AwayTeamSubNum','AwayTeamSubName',
                                'AwayTeamSubSlug','AwayTeamSubNationalite','AwayTeamSubLien'
                                ])
data.replace('Manchester City','Man City',inplace=True)
data.replace('Manchester Utd','Man United',inplace=True)
data.replace('Sheffield Utd','Sheffield United',inplace=True)
data['Saison']=data.Date.apply(lambda x: int(x.split('-')[2]))
data.Date = pd.to_datetime(data.Date,dayfirst =True)
data['Cle']= data.Date.map(str).apply(lambda x : x[:10])+'/'+data.HomeTeam+'/'+data.AwayTeam
df['Cle']= df.Date.map(str).apply(lambda x : x[:10])+'/'+df.HomeTeam+'/'+df.AwayTeam
df=pd.merge(df,data[['Cle','Heure']],how='left',on='Cle')
df.drop('Cle',axis=1,inplace=True)
df = df[(df.Div == 'E0') & (df.Saison >2009)]
df['DateHeure'] = pd.to_datetime(df.Date.map(str).apply(lambda x : x[:10]) + ' '+ df.Heure,dayfirst=True)
df.to_excel('Data/Base.xlsx')
pd.DataFrame(lst_error,columns=['url']).to_csv('Data/urlbugScrapper.csv')
data = pd.DataFrame(lst,columns=['Date','Heure','HomeTeam','AwayTeam','HomeTeamStartNum','HomeTeamStartName',
                                'HomeTeamStartSlug','HomeTeamStartNationalite','HomeTeamStartLien',
                                 'AwayTeamStartNum','AwayTeamStartName','AwayTeamStartSlug','AwayTeamStartNationalite',
                                 'AwayTeamStartLien','HomeTeamSubNum','HomeTeamSubName',
                                'HomeTeamSubSlug','HomeTeamSubNationalite','HomeTeamSubLien','AwayTeamSubNum','AwayTeamSubName',
                                'AwayTeamSubSlug','AwayTeamSubNationalite','AwayTeamSubLien'
                                ])
data.to_csv('Data/SoccerBoardBase.csv')