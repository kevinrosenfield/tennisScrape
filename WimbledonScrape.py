from selenium import webdriver
#import chromedriver_binary  # Adds chromedriver binary to path
import time
from bs4 import BeautifulSoup
import bs4
import numpy as np
import re
import pandas as pd
import csv

def boxStats(slamSoup, allStats1, allStats2):
    matchBox = slamSoup.find('div', {"class":"match-box live"}) 
    event = matchBox.find("span", {"class":"event-round"}).text
    team1 = matchBox.find('div', {"class":"team-info team-one singles"})
    name1 = team1.find('div', {"class":"member-one name-link"}).find('div', {"class":"name"}).text
    seed1 = team1.find('div', {"class":"member-one name-link"}).find('div', {"class":"seed"}).text
    team1_sets = []
    for sets in list(range(1,6)):
        team1_sets += [team1.find('div', {"class":"set set" + str(sets)}).text]
    if team1_sets[4] == '':
        team1_sets[4] = float('nan') 
    if team1_sets[3] == '':
        team1_sets[3] = float('nan')
    team2 = matchBox.find('div', {"class":"team-info team-two singles"})
    name2 = team2.find('div', {"class":"member-one name-link"}).find('div', {"class":"name"}).text
    seed2 = team2.find('div', {"class":"member-one name-link"}).find('div', {"class":"seed"}).text
    team2_sets = []
    emptySets = 0
    for set in list(range(1,6)):
        team2_sets += [team2.find('div', {"class":"set set" + str(set)}).text]
    if team2_sets[4] == '':
        emptySets = 1
        team2_sets[4] = float('nan')
    if team2_sets[3] == '':
        emptySets = 2
        team2_sets[3] = float('nan')
    if team1_sets[-1 - emptySets] > team2_sets[-1 - emptySets]:
        outcome1 = 'W'
        outcome2 = 'L'
    else:
        outcome1 = 'L'
        outcome2 = 'W'
    if len(team1_sets) == 2:
        team1_sets += [float('nan'), float('nan'), float('nan')]
    elif len(team1_sets) == 3:
        team1_sets += [' ', ' ']
    elif len(team1_sets) == 4:
        team1_sets += [' ']
    if len(team2_sets) == 2:
        team2_sets += [' ', ' ', ' ']
    elif len(team2_sets) == 3:
        team2_sets += [' ', ' ']
    elif len(team2_sets) == 4:
        team2_sets += [' ']
    allStats1 += [event, name1, seed1, *team1_sets, outcome1, float('nan')]
    if allStats1[6] == '':
        allStats1[6] = float('nan')
    allStats2 += [event, name2, seed2, *team2_sets, outcome2, float('nan')]
    if allStats2[6] == '':
        allStats2[6] = float('nan')

def statsButton(slamTracker):
    cookieButton = slamTracker.find_element_by_xpath("//i[@class='icon-close']")
    cookieButton.click()
    statsButton = slamTracker.find_element_by_xpath("//div[@class='full-stats-button']")
    statsButton.click()

def getReturn(matchDriver, slamTracker, allStats1, allStats2):
    returnStatsButton = matchDriver.find_element_by_xpath("//a[@data-ref='Return Stats']")
    returnStatsButton.click()
    returnSoup = BeautifulSoup(slamTracker.get_attribute('innerHTML'), features="lxml")
    returnList = []    
    for row in returnSoup.find('div', {"class":"stats-table-wrapper return"}).find_all('div', {"class":"stats-row"}):
        for stat in row.find_all(['div', 'span']):
            returnList += stat
            for stat in returnList:
                if isinstance(stat, bs4.element.Tag):
                    returnList.remove(stat)
    returnIndices1 = np.r_[:3,7:10,14:17,21:24]
    allStats1 += list(np.array(returnList)[returnIndices1]) + list([' '])
    returnIndices2 = np.array([i + 4 for i in returnIndices1])
    allStats2 += list(np.array(returnList)[returnIndices2]) + list([' '])

def getServe(matchDriver, slamTracker, allStats1, allStats2):
    serveStatsButton = matchDriver.find_element_by_xpath("//a[@data-ref='Serve Stats']")
    serveStatsButton.click()
    serveSoup = BeautifulSoup(slamTracker.get_attribute('innerHTML'), features="lxml")
    serveList = []
    for row in serveSoup.find('div', {"class":"stats-table-wrapper serve"}).find_all('div', {"class":"stats-row"}):
        for stat in row.find_all(['div', 'span']):
            serveList += stat
            for stat in serveList:
                if isinstance(stat, bs4.element.Tag) or stat == ' ' or 'KMH' in stat:
                    serveList.remove(stat)
    serveIndices1 = np.r_[:3,7:10,16:17,21:24,28:31,37:38,42:45,49:52]
    allStats1 += list(np.array(serveList)[serveIndices1])
    serveIndices2 = np.array([i + 4 for i in serveIndices1])
    allStats2 += list(np.array(serveList)[serveIndices2])
    

def getStats(matchDriver, slamTracker, allStats1, allStats2):
    overallStatsButton = matchDriver.find_element_by_xpath("//a[@data-ref='Overall Stats']")
    overallStatsButton.click()
    statsList = []
    slamSoup = BeautifulSoup(slamTracker.get_attribute('innerHTML'), features="lxml")
    for table in slamSoup.find('div', {"class":"stats-table-wrapper overall matchstats"}):
        for stat in table.find_all('div', {"class": re.compile(r'^stats-data')}):
            statsList += stat
        for span in table.find_all('span', {"class": 'imperial'}):
            statsList += span
            for stat in statsList:
                if isinstance(stat, bs4.element.Tag):
                    statsList.remove(stat)
    statsIndices1 = np.r_[6,10,12,16,18,20]
    allStats1 += list(np.array(statsList)[statsIndices1]) + list([' '])
    try:
        allStats1 += list(np.array(statsList)[np.r_[22]])
        try:
            allStats1 += list(np.array(statsList)[np.r_[24]])
        except IndexError:
            allStats1 += [' ']
    except IndexError:
        allStats1 += [' ', ' ']
    statsIndices2 = np.array([i + 1 for i in statsIndices1])
    allStats2 += list(np.array(statsList)[statsIndices2]) + list([' '])
    try:
        allStats2 += list(np.array(statsList)[np.r_[23]])
        try:
            allStats2 += list(np.array(statsList)[np.r_[25]])
        except IndexError:
            allStats2 += [' ']
    except IndexError:
        allStats2 += [' ', ' ']
    
def getMatch(matchURL, matchID, allStats):
    matchDriver = webdriver.Chrome('/Users/kevinrosenfield/downloads/chromedriver', options = options)
    matchDriver.get(matchURL)
    matchDriver.maximize_window()
    #matchHTML = matchDriver.page_source
    time.sleep(0.5)
    slamTracker = matchDriver.find_element_by_xpath("//div[@class='slamtracker-content']")
    slamSoup = BeautifulSoup(slamTracker.get_attribute('innerHTML'), features="lxml")
    allStats1 = ['Wimbledon', ' 2019.07.01 - 2019.07.14 ', 128, 'Grass']
    allStats2 = ['Wimbledon', ' 2019.07.01 - 2019.07.14 ', 128, 'Grass']
    boxStats(slamSoup, allStats1, allStats2)
    statsButton(slamTracker)
    getServe(matchDriver, slamTracker, allStats1, allStats2)
    slamTracker = matchDriver.find_element_by_xpath("//div[@class='slamtracker-content']")
    getStats(matchDriver, slamTracker, allStats1, allStats2)
    getReturn(matchDriver, slamTracker, allStats1, allStats2)
    allStats.update({matchID + '-1': allStats1, matchID + '-2': allStats2})
    for match, stats in allStats.items():
        print(match, len([item for item in stats if item]))
        print(stats)
    matchDriver.quit()

def getMatchList(driver, stats):
    allStats = {'matchID':stats}
    for day in days[0:1]:
        driver.get("https://www.wimbledon.com/en_GB/scores/results/day" + str(day) + ".html")
        html = driver.page_source
        soup = BeautifulSoup(html, features="lxml")
        for match in soup.find_all('div', {"class":"match-box"}):
            if "Gentlemen's Singles" in match.text:
                matchID = str(match)[66:70]
                matchURL = 'https://www.wimbledon.com/en_GB/scores/stats/' + matchID + '.html'
                #try:
                getMatch(matchURL, matchID, allStats)
                #except:
                #    pass
    allStatsDF = pd.DataFrame(allStats).T
    return(allStatsDF)

stats = ['tournament', 'dates', 'bracketSize', 'surface', 'round', 'player', 'seeding', 'set1', 'set2', 'set3',
         'set4', 'set5', 'outcome', 'serveRating', 'firstAces', 'secondAces', 'totalAces', 'firstServeWinners',
         'secondServeWinners', 'totalServeWinners', 'doubleFaults',
         'firstServePointsPlayed', 'secondServePointsPlayed', 'totalServePointsPlayed', 'firstServePointsWon',
         'secondServePointsWon', 'totalServePointsWon', 'numberServeGames', 'firstMeanServeSpeed',
         'secondMeanServeSpeed', 'totalMeanServeSpeed', 'firstFastestServeSpeed', 'secondFastestServeSpeed',
         'totalFastestServeSpeed', 'firstServe%', 'netPointsWon', 'breakPointsConverted', 'winners', 'unforcedErrors', 'totalPointsWon',
         'ReturnRating','distanceCovered', 'distanceCoveredPerPoint', 'firstReturnWinners', 'secondReturnWinners', 
         'totalReturnWinners', 'firstReturnUnforced', 'secondReturnUnforced', 'totalReturnUnforced',
         'firstReturnPointsPlayed', 'secondReturnPointsPlayed', 'totalReturnPointsPlayed', 'firstReturnPointsWon',
         'secondReturnPointsWon', 'totalReturnPointsWon', 'ReturnGamesPlayed']

days = list(range(8,22))
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')

driver = webdriver.Chrome('/Users/kevinrosenfield/downloads/chromedriver', options = options)
allStatsDF = getMatchList(driver, stats)
allStatsDF.to_csv("wimbledonStats1.csv", index=True)
driver.quit()

# add rank
# make player file with height, handedness, DOB; weight???
