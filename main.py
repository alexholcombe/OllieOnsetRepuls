#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


"""

from psychopy import monitors, visual, event, data, logging, core, sound, gui
import psychopy.info
import numpy as np
from math import atan, log, ceil
from copy import deepcopy
import time, sys, os#, pylab
import string
from random import random

quitFinder=False
refreshRate = 60.0

monitorname = 'testmonitor'
widthPixRequested= 1024 #monitor width in pixels of Agosta
heightPixRequested= 768 #800 #monitor height in pixels
monitorwidth = 40.5 #monitor width in cm
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
fullscr=False #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
viewdist = 57. #cm
bgColor = [-.7,-.7,-.7] # [-1,-1,-1]


waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPixRequested,heightPixRequested) )
units='deg' #'cm'
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPixRequested,heightPixRequested),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin

# create a dialog from dictionary 
infoFirst = { 'Do staircase (only)': False, 'Check refresh etc':False, 'Fullscreen (timing errors if not)': False, 'Screen refresh rate': 60 }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='AB or dualstream experiment OR staircase to find thresh noise level for T1 performance criterion', 
    order=['Do staircase (only)', 'Check refresh etc', 'Fullscreen (timing errors if not)'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating'},
    #fixed=['Check refresh etc'])#this attribute can't be changed by the user
    )
if not OK.OK:
    print('User cancelled from dialog box'); core.quit()
doStaircase = infoFirst['Do staircase (only)']
checkRefreshEtc = infoFirst['Check refresh etc']
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']
if checkRefreshEtc:
    quitFinder = True 
if quitFinder:
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)

myWin= openMyStimWindow()

if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
    refreshRateWrong = False
else: #checkRefreshEtc
    runInfo = psychopy.info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    #print(runInfo)
    logging.info(runInfo)
    print('Finished runInfo- which assesses the refresh and processes of this computer') 
    #check screen refresh is what assuming it is ##############################################
    Hzs=list()
    myWin.flip(); myWin.flip();myWin.flip();myWin.flip();
    myWin.setRecordFrameIntervals(True) #otherwise myWin.fps won't work
    print('About to measure frame flips') 
    for i in range(50):
        myWin.flip()
        Hzs.append( myWin.fps() )  #varies wildly on successive runs!
    myWin.setRecordFrameIntervals(False)
    # end testing of screen refresh########################################################
    Hzs = np.array( Hzs );     Hz= np.median(Hzs)
    msPerFrame= 1000./Hz
    refreshMsg1= 'Frames per second ~='+ str( np.round(Hz,1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    myWinRes = myWin.size
    myWin.allowGUI =True
myWin.close() #have to close window to show dialog box

demo=False
autopilot=False
trialsPerCondition = 1
subject='Herbert'
session='a'
#Create new dialog box, with results of timing test and with experiment parameters to set like subject name and session
dlgLabelsOrdered = list() #new dialog box
session='a'
myDlg = psychopy.gui.Dlg(title="onset repulsion experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name or ID:', subject, tip='')
    dlgLabelsOrdered.append('subject')
    myDlg.addField('session:',session, tip='a,b,c,')
    dlgLabelsOrdered.append('session')
myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', trialsPerCondition, tip=str(trialsPerCondition))
dlgLabelsOrdered.append('trialsPerCondition')
pctCompletedBreaks = np.array([])
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
msgWrongResolution = ''
if checkRefreshEtc and (not demo) and (myWinRes != [widthPixRequested,heightPixRequested]).any():
    msgWrongResolution = 'Instead of desired resolution of '+ str(widthPixRequested)+'x'+str(heightPixRequested)+ ' pixels, screen apparently '+ str(myWinRes[0])+ 'x'+ str(myWinRes[1])
    myDlg.addText(msgWrongResolution, color='GoldenRod')
    print(msgWrongResolution)
myDlg.addText('To abort, press ESC at a trial response screen', color='DimGrey') #color names stopped working along the way, for unknown reason
myDlg.show()
if myDlg.OK: #unpack information from dialogue box
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
       sessionEntered =thisInfo[dlgLabelsOrdered.index('session')]
       session = str(sessionEntered) #cast as str in case person entered a number
   trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()



# create your list of stimuli
# NB as of version 1.62 you could simply import an excel spreadsheet with this
# using data.importConditions('someFile.xlsx')
stimList = []
for circleRadius in range(3, 20, 5):
    for direction in [-1,1]:
        # append a python 'dictionary' to the list
        stimList.append({'circleRadius': circleRadius, 'direction':direction})

print(stimList)
# organize them with the trial handler
trials = data.TrialHandler(stimList, 10,
                           extraInfo={'participant': "Nobody", 'session':'001'})


myWin = openMyStimWindow()

# Create a circle stimulus
circle = visual.Circle(
    win=myWin,
    radius=50,  # Radius 
    edges=128,  # Number of edges to approximate the circle
    fillColor='white'  # Fill color
    #lineColor='black'  # Line color
)

stimDur = 0.3
stimDurFrames = int( np.floor(stimDur / (1./refreshRate)) )

# run the experiment
nDone = 0
for thisTrial in trials:  # handler can act like a for loop
    # simulate some data
    circle.radius =  thisTrial['circleRadius']
    for frame in range(stimDurFrames):
        circle.draw()
        myWin.flip()
        
    thisReactionTime = random() 
    thisChoice = round(random())
    trials.data.add('RT', thisReactionTime)  # add the data to our set
    trials.data.add('choice', thisChoice)
    nDone += 1  # just for a quick reference

    msg = 'trial %i had position %s in the list (circleRadius=%.1f)'
    print(msg % (nDone, trials.thisIndex, thisTrial['circleRadius']))

# After the experiment, print a new line
print('\n')

# Write summary data to screen
trials.printAsText()

# Write summary data to a text file ...
trials.saveAsText(fileName='testData')

# ... or an xlsx file (which supports sheets)
trials.saveAsExcel(fileName='testData')

# Save a copy of the whole TrialHandler object, which can be reloaded later to
# re-create the experiment.
trials.saveAsPickle(fileName='testData')

# Wide format is useful for analysis with R or SPSS.
df = trials.saveAsWideText('testDataWide.txt')
