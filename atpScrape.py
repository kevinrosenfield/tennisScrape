import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
#import csv
#from datetime import datetime
        

def getStats(matchSoup, leftValues, rightValues, matchID):
        
        for tr in matchSoup.find_all('tr', {"class": "match-stats-row percent-on"}):

            text = []
            for left in tr.find('td', {"class": "match-stats-number-left"}).find_all('span'):
                text.append(re.sub('\r','',  re.sub('\n','', re.sub(' ','', left.text))))
            leftValues += ['-'.join(text)]
                
            text = []
            for right in tr.find('td', {"class": "match-stats-number-right"}).find_all('span'):
                text.append(re.sub('\r','', re.sub('\n','', re.sub(' ','', right.text))))
            rightValues += ['-'.join(text)]
        
        blanks = [6,14,15,17,18,19,21,22,23,27,28,29,30,31,32,33,38] + list(range(45,57)) 
        
        for blank in blanks:
            leftValues.insert(blank, float('nan'))
            rightValues.insert(blank, float('nan'))
        
        newOrder = list(range(24)) + [25,26,42,35] + list(range(27,33)) + [24,33,40,38,45,
                       44,36] + list(range(46,57)) + [37,39,43,41]
        
        tempListL = []
        for col in newOrder:
            tempListL.append(leftValues[col])
            
        tempListR = []
        for col in newOrder:
            tempListR.append(rightValues[col])
        
        leftValues = tempListL
        rightValues = tempListR
        
        d = {matchID + '-1':leftValues, matchID + '-2':rightValues}
                
        return(d)
        
        
def getSets(matchSoup, leftValues, rightValues, matchID):
    
    allSets = []
    for tr in matchSoup.find('table', {"class": "scores-table"}).find('tbody').find_all('tr')[0:2]:
        for td in tr.find_all('td')[1:]:
            allSets += [re.sub('\r','',  re.sub('\n','', re.sub(' ','', td.text)))]
    numSets = int(len(allSets)/2 - 2)
    emptySets = [' '] * (5 - numSets)
    rightSets = allSets[numSets + 3:-1]
    leftSets = allSets[1:numSets + 1]
    leftValues += leftSets
    rightValues += rightSets
    if leftSets[-1] > rightSets[-1]:
        leftOutcome = "W"
        rightOutcome = "L"
    else:
        leftOutcome = "L"
        rightOutcome = "W"
    for i in emptySets:
        leftValues += ' '
        rightValues += ' '
    leftValues += leftOutcome
    rightValues += rightOutcome
        
    
def getMatch(matchURL, tournament, dates, bracketSize, surface):
    
    matchPage = requests.get(matchURL)
    matchSoup = BeautifulSoup(matchPage.content, 'html.parser')
    leftValues = [tournament, dates, bracketSize, surface]
    rightValues = [tournament, dates, bracketSize, surface]
    event = matchSoup.find('div', {"class":"scoring-section"}).find('caption', {"class":"match-title"}).text
    matchID = matchURL[39:49]

    if matchSoup.find('div', {"class": "player-left-name"}) is None:

        d = {matchID + '-1':noData, matchID + '-2':noData}

    else:
        leftNameLoc  = matchSoup.find('div', {"class": "player-left-name"})
        leftName = leftNameLoc.find('span', {"class": "last-name"}).text + "," + leftNameLoc.find('span', {"class": "first-name"}).text
        leftName = re.sub('\r','', re.sub('\n','', re.sub(' ','', leftName)))
    
        rightNameLoc  = matchSoup.find('div', {"class": "player-right-name"})
        rightName = rightNameLoc.find('span', {"class": "last-name"}).text + "," + rightNameLoc.find('span', {"class": "first-name"}).text
        rightName = re.sub('\r','', re.sub('\n','', re.sub(' ','', rightName)))
    
        leftValues.append(re.sub('\r','',  re.sub('\n','', re.sub(' ','', re.sub('H2H','', event)))))
        rightValues.append(re.sub('\r','',  re.sub('\n','', re.sub(' ','', re.sub('H2H','', event)))))
        leftValues.append(re.sub('\r','',  re.sub('\n','', re.sub(' ','', leftName))))
        rightValues.append(re.sub('\r','',  re.sub('\n','', re.sub(' ','', rightName))))

        getSets(matchSoup, leftValues, rightValues, matchID)
        d = getStats(matchSoup, leftValues, rightValues, matchID)
            
    for key, value in d.items():
        if len([item for item in value if item]) == 0:
            leftValues = noData
            rightValues = noData
            d = {matchID + '-1':leftValues, matchID + '-2':rightValues}
    return(d)


def getPlayer(playerURL):
    playerPage = requests.get(playerURL)
    playerSoup = BeautifulSoup(playerPage.content, 'html.parser')
    playerName = playerURL[35:-30]
    print(playerName)

    for table in playerSoup.find_all('div', {"class":"activity-tournament-table"})[0:1]:
        tournament = table.find('a', {"class": "tourney-title"}).text
        tournament = re.sub('\r','', re.sub('\n','', re.sub(' ','', tournament)))
        dates = table.find('span', {"class": "tourney-dates"}).text
        dates = re.sub('\r','', re.sub('\n','', re.sub(' ','', dates)))
        bracketSize = table.find_all('span', {"class": "item-value"})[1].text
        bracketSize = re.sub('\r','', re.sub('\n','', re.sub(' ','', bracketSize)))
        surface = table.find_all('span', {"class": "item-value"})[2].text
        surface = re.sub('\r','', re.sub('\n','', re.sub(' ','', surface)))
        matchLinks = []
        matchLinks = table.find_all('a', {"class":""}, {"ga-use":"true"})
        for link in matchLinks:
            matchURL = 'https://www.atptour.com'+ link.get('href')
            matchStats = []
            matchStats = getMatch(matchURL, tournament, dates, bracketSize, surface)
            careerStats.update(matchStats)
    return(careerStats)
    
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

noData = ['noData'] * len(stats)
careerStats = {'matchID':stats}

atpURL = 'https://www.atptour.com/en/rankings/singles?rankDate=2020-03-16&rankRange=1-1'
atpPage = requests.get(atpURL)
atpSoup = BeautifulSoup(atpPage.content, 'html.parser')

for player in atpSoup.find_all('td', {"class":"player-cell"}):
    playerLink = player.find('a')
    playerURL = playerLink.get('href')
    playerURL = 'https://www.atptour.com'+ re.sub('overview', 'player-activity?year=all', playerURL)
    careerStats = getPlayer(playerURL)

for key, value in careerStats.items():
    print(key, len([item for item in value if item]))

df = pd.DataFrame(careerStats).T
df.to_csv("tennisStats.csv", index=True)
