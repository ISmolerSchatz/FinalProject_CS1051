## Isaac Smoler Schatz
## CS 1051
## Final Project - NYT Crossword Puzzle Black Box Analysis
## Crossword puzzle data via xwordinfo.com archive

import requests
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer as ss
import random
import datetime
import pygame

dotwEvalOptions = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'all_non_sun']
dayType = input("Enter one of the options below to evaluate crossword puzzles from that day(s): \n (sun, mon, tue, wed, thu, fri, sat, all_non_sun) \n")
while (dayType not in dotwEvalOptions):
    dayType = input("Enter one of the options below to evaluate crossword puzzles from that day(s): \n (sun, mon, tue, wed, thu, fri, sat, all_non_sun) \n")

print("Note that evaluating 100 puzzles takes approximately 1 minute.")
boardsToEval = int(input("How many crossword puzzle boards should be evaluated?: "))
while (boardsToEval > 1000):
    boardsToEval = int(input("How many crossword puzzle boards should be evaluated?: "))

## creates the dates for 1/1/1994 - 12/31/2020 (16 years)
allDates = []
for year in range(1994,2021):
    for month in range(1,13):
        for day in range(1,32):
            if day <= 28:
                allDates.append(str(month) + '/' + str(day) + '/'+ str(year))
            elif day == 29:
                if month != 2:
                    allDates.append(str(month) + '/' + str(day) + '/'+ str(year))
                elif year % 4 == 0:
                    allDates.append(str(month) + '/' + str(day) + '/'+ str(year))
            elif day == 30:
                if month != 2:
                    allDates.append(str(month) + '/' + str(day) + '/'+ str(year))
            elif day == 31:
                if month in [1,3,5,7,8,10,12]:
                    allDates.append(str(month) + '/' + str(day) + '/'+ str(year))

## creates the dateLists based on dayType
sunDates = allDates[1::7]
monDates = allDates[2::7]
tueDates = allDates[3::7]
wedDates = allDates[4::7]
thuDates = allDates[5::7]
friDates = allDates[6::7]
satDates = allDates[::7]
all_non_sunDates = [x for i, x in enumerate(allDates) if i%7 !=1]
dotwDatesList = [sunDates, monDates, tueDates, wedDates, thuDates, friDates, satDates, all_non_sunDates]

# creates a list of dates whose puzzles have nonrectangular grids
nonRect = ['7/16/2019', '1/6/2015', '9/25/2012', '11/2/2004', '2/14/2018', '10/30/2014', '1/21/2010', '2/2/1995']


## removes dates with nonrectangular boards from dateLists
for dotwDates in dotwDatesList:
    for badDate in nonRect:
        if badDate in dotwDates:
            dotwDates.remove(badDate)


## sets dateList and creates empty bbHeatMapDict based on dayType
if dayType == "sun":
    size = 21
    dateList = sunDates
else:
    size = 15
    if dayType == "mon":
        dateList = monDates
    elif dayType == "tue":
        dateList = tueDates
    elif dayType == "wed":
        dateList = wedDates
    elif dayType == "thu":
        dateList = thuDates
    elif dayType == "fri":
        dateList = friDates
    elif dayType == "sat":
        dateList = satDates
    else:
        dateList = all_non_sunDates
bbHeatMapDict = {}
for x in range(size):
    bbHeatMapDict[x] = {}
    for y in range(size):
        bbHeatMapDict[x][y] = 0
print("The standard grid has dimensions", str(size)+"x"+str(size))


## populates the bbHeatMapDict for the cells in the puzzle on a given date
def bbHeatMapEval(date, size, puzzlesEvaluated):
    puzzleLink = "https://www.xwordinfo.com/Crossword?date=" + date
    puzzle = requests.get(puzzleLink)
    # populates bbHeatMapDict for evaluated puzzle
    tablesoup = bs(puzzle.content, 'html.parser', parse_only = ss(id="PuzTable"))
    rowsoup = tablesoup.find_all('tr')
    num_rows = len(rowsoup)
    cellsoup = tablesoup.find_all('td')
    num_cols = len(cellsoup)//len(rowsoup)
    if num_rows != size or num_cols != size:
        print("Crossword puzzle board for", date, "is nonstandard size!")
        return puzzlesEvaluated
    bbNum = 0
    for x in range(len(rowsoup)):
        cellsoup = rowsoup[x].find_all('td')
        cellList = str(cellsoup).split(',')
        for y in range(len(cellList)):
            if 'class="black"' in cellList[y]:
                bbNum += 1
                bbHeatMapDict[x][y] += 1
    bbNumList.append(bbNum)
    datesEvaluated.append(date)
    puzzlesEvaluated += 1
    if puzzlesEvaluated%5 == 0:
        print(puzzlesEvaluated, "puzzles evaluated so far")
    return puzzlesEvaluated


## calls the bbHeatMapEval function for dates in the given dateList as many times as there are boardsToEval
bbNumList = []
datesEvaluated = []
puzzlesEvaluated = 0
i = 0
while (puzzlesEvaluated != boardsToEval):
    date = random.choice(dateList)
    #print(date)
    puzzlesEvaluated = bbHeatMapEval(date, size, puzzlesEvaluated)
    dateList.remove(date)
    i += 1
    

#### prints the results of the bbHeatMapEval 
### bbHeatMapDict as an array
##grid = []
##for row in range(size):
##    grid.append([])
##    for column in range(size):
##        bbpct = round(bbHeatMapDict[row][column]/puzzlesEvaluated*100, 2)
##        grid[row].append(bbpct)
##    print(grid[row], end = "\n")
# average bb per board
bbNumTotal = 0
for bbSum in bbNumList:
    bbNumTotal += bbSum
bbAVG = round(bbNumTotal/puzzlesEvaluated)
bbAVGcoveragePCT = round(bbAVG/(size**2)*100, 2)
print("There were an average of", bbAVG, "black squares per board among the", boardsToEval, dayType, "puzzles you evaluated!")
print("Therefore, approximately", bbAVGcoveragePCT, "percent of the squares on each", dayType, "puzzle are black")

## ask the user if they want to see the dates evaluated
viewDatesQ = input("Do you want to see the dates of the evaluated puzzles? Y/YES/N/NO: ")
validResponse = ['Y','YES','N','NO']
def viewState(response):
    capResponse = response.upper()
    if (capResponse not in validResponse):
        print("Enter Y, YES, N, or NO")
        return False
    elif (capResponse in ['Y','YES']):
        datesEvalSorted = sorted(datesEvaluated, key=lambda x: datetime.datetime.strptime(x, '%m/%d/%Y'))
        for i in datesEvalSorted:
            print(i)
        return True
    else:
        return True
while (viewState(viewDatesQ) == False):
    viewDatesQ = input("Do you want to see the dates of the evaluated puzzles? Y/YES/N/NO: ")


#################################### pygame section!!!
### This section references tutorial code from
### http://programarcadegames.com/index.php?lang=en&chapter=array_backed_grids

# color = ( R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
# sets the WIDTH and HEIGHT of each grid location and MARGIN between them
WIDTH = 30
HEIGHT = 30
MARGIN = 3
# creates 2D array for display status
viewgrid = []
for row in range(size):
    # Add an empty array that will hold each cell
    # in this row
    viewgrid.append([])
    for column in range(size):
        viewgrid[row].append(0)  # Append a cell
 
# Initialize pygame
pygame.init()
# sets the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [size*(33)+3, size*(33)+3]
screen = pygame.display.set_mode(WINDOW_SIZE)
# Set title of screen
pygame.display.set_caption("NYT Crossword Puzzle Black Box Analysis")
myFont = pygame.font.SysFont("Times New Roman", 12)
# Loop until the user clicks the close button
done = False
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
while not done:
    for e in pygame.event.get():  # User did something
        if e.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
        elif e.type == pygame.MOUSEBUTTONDOWN:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)
            # increment that location by 1
            viewgrid[row][column] += 1
            print("Click ", pos, "Grid coordinates: ", row, column)
 
    # sets the screen background
    screen.fill(BLACK)
    # draws the heatmap grid
    for x in range(size):
        for y in range(size):
            GRADIENT = 255 - round(bbHeatMapDict[x][y]/puzzlesEvaluated*255)
            color = (GRADIENT, GRADIENT, GRADIENT)
            # adds the percent bb at click
            if (viewgrid[row][column])%2 == 1:
                bbpct = round(bbHeatMapDict[row][column]/puzzlesEvaluated*100, 2)
                bbpctLabel = myFont.render(str(bbpct)+"%", 1, RED)
                screen.blit(bbpctLabel, (pos[0], pos[1]))
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * y + MARGIN,
                              (MARGIN + HEIGHT) * x + MARGIN,
                              WIDTH,
                              HEIGHT])

    # Limit to 60 frames per second
    clock.tick(60)
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip() 
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()
