from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
def getNextOdds(journee):
    """
        Input : 
            journee : Integer, récupère les cotes pour une journée à venir défini.
        Ouput: 
            bets : DataFrame, contient toutes les cotes (HW,D,AW) de winamax pour les matchs de la journée choisie
            
    """
    driver = webdriver.Chrome('C:/Users/franc/Desktop/Cours/chromedriver.exe')
    driver.get('https://www.flashresultats.fr/football/angleterre/premier-league/calendrier/')
    soup = BeautifulSoup(driver.page_source,'lxml')
    day = 'Journée '+str(journee)
    lst=[]
    for matchday in soup.find('div',id='live-table').find_all('div',class_='event__round event__round--static'):
        if (matchday.text == day):
            data = matchday.nextSibling
            while not 'Journée' in data.text:
                idm =data.attrs['id'].replace('g_1_','')
                HomeTeam = data.find("div",class_='event__participant event__participant--home').text
                AwayTeam = data.find("div",class_='event__participant event__participant--away').text
                date = data.find('div',class_='event__time').text.split(" ")[0].replace('.','/')+str(2020)
                url = 'https://www.flashresultats.fr/match/'+idm+'/#comparaison-des-cotes;cotes-1x2;temps-regulier'
                driver.get(url)
                time.sleep(2)
                html =BeautifulSoup(driver.page_source,'lxml')
                for tr in html.find('table',class_='odds sortable').find_all('tr')[1:]:
                    if tr.find('a').attrs['title']== 'Winamax':
                        cH = tr.find_all('span',class_='odds-wrap')[0].text
                        cD = tr.find_all('span',class_='odds-wrap')[1].text
                        cA = tr.find_all('span',class_='odds-wrap')[2].text
                lst+=[(HomeTeam,AwayTeam,date,cH,cD,cA)]
                data = data.nextSibling
    bets = pd.DataFrame(lst,columns=["HomeTeam","AwayTeam","Date","B365H","B365D","B365A"])
    driver.quit()
    return bets