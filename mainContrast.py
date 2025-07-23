#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


"""
import helpersAOH
from psychopy import monitors, visual, event, data, logging, core, sound, gui
import psychopy.info
import numpy as np
from math import atan, log, ceil, sqrt
from copy import deepcopy
import time, sys, os#, pylab
import string, platform
from random import random
from random import choice
try:
    import stringResponse
except ImportError:
    print('Could not import stringResponse.py (you need that file to be in the same directory)')
quitFinder=False
refreshRate = 60.0
autoLogging = True
process_priority = 'realtime' # 'normal' 'high' or 'realtime', but don't know if this works
disable_gc = True

monitorname = 'testmonitor'
widthPixRequested= 1920 #1600 #monitor width in pixels
heightPixRequested= 1080 #800 #monitor height in pixels
monitorwidth = 28.6 #monitor width in cm
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
fullscr= True #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
viewdist = 25 #cm
bgColor = [0,0,0] # [-1,-1,-1]
useRetina=True

#####################################################################
#Do an initial test of the screen refresh rate and resolution
waitBlank = False
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#relying on  monitorwidth cm (39 for Mitsubishi to do deg calculations) and gamma info in calibratn
mon.setSizePix( (widthPixRequested,heightPixRequested) )
units='deg' #'cm'
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPixRequested,heightPixRequested),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin

#Find out if screen may be Retina because of bug in psychopy for mouse coordinates (https://discourse.psychopy.org/t/mouse-coordinates-doubled-when-using-deg-units/11188/5)
has_retina_scrn = True
mon.setSizePix((widthPixRequested // 1.315, heightPixRequested // 1.315))
import subprocess
if 'Darwin' in platform.system(): #Because want to run Unix commands, which won't work on Windows - only do it if Mac
    resolutionOfScreens = subprocess.check_output("system_profiler SPDisplaysDataType | grep -i 'Resolution'",shell=True)
    print("resolution of screens reported by system_profiler = ",resolutionOfScreens)
    if subprocess.call("system_profiler SPDisplaysDataType | grep -i 'retina'", shell=True) == 0:
        has_retina_scrn = True #https://stackoverflow.com/questions/58349657/how-to-check-is-it-a-retina-display-in-python-or-terminal
dlgBoxTitle = 'Oliver honours, and no Mac Retina screen detected'
if has_retina_scrn:
    dlgBoxTitle = 'Oliver honours. At least one screen is apparently a Retina screen'
    
# create a dialog from dictionary 
infoFirst = { 'Do staircase (only)': False, 'Check refresh etc':False, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate': refreshRate }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title=dlgBoxTitle, 
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

#############################################################################################
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

if os.path.isdir('.'+os.sep+'dataRaw'):
    dataDir='dataRaw'
else:
    print('"dataRaw" directory does not exist, so saving data in present working directory')
    dataDir='.'
expname = ''

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
datafileName = dataDir+'/'+subject+ '_' + str(session) + '_' + expname+timeAndDateStr
if not demo: #Create log for timing blips etc.
    logF = logging.LogFile(datafileName+'.log', 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile

#realtime timing check parameters
differentFromRefreshTolerance = 0.15 #0.27
longFrameLimit = round(1000./refreshRate*(1.0+differentFromRefreshTolerance),3) # round(1000/refreshRate*1.5,2)
msg = 'longFrameLimit=' + str(longFrameLimit) + ' Recording trials where one or more interframe interval exceeded this figure '
logging.info(msg)
print(msg)
shortFrameLimit = round(1000./refreshRate*(1.0-differentFromRefreshTolerance),3) # round(1000/refreshRate*1.5,2)
msg = 'shortFrameLimit=' + str(shortFrameLimit) + ' Recording trials where one or more interframe interval too short, shorter than this figure'
logging.info(msg)

logging.info("computer platform="+sys.platform)
#save a copy of the code as it was when that subject was run
logging.info('File that generated this = sys.argv[0]= '+sys.argv[0])
logging.info("has_retina_scrn="+str(has_retina_scrn))


# Create list of stimuli
# NB as of version 1.62 you could simply import an excel spreadsheet with this
# using data.importConditions('someFile.xlsx')
stimList = []
radiusMin = 3; radiusMax = 15
for circleRadius in range(radiusMin, radiusMax, 5):
    for direction in [-1,1]:
        # append a python 'dictionary' to the list
        stimList.append({'circleRadius': circleRadius, 'direction':direction})

print(stimList)
# organize them with the trial handler
trials = data.TrialHandler(stimList, 10,
                           extraInfo={'participant': "Nobody", 'session':'001'})

myWin = openMyStimWindow()

#Create flickering fixation point of random noise
fixatnNoise = True
fixSizePix = 20 #6 make fixation big so flicker more conspicuous
if fixatnNoise:
    checkSizeOfFixatnTexture = fixSizePix/4
    nearestPowerOfTwo = round( sqrt(checkSizeOfFixatnTexture) )**2 #Because textures (created on next line) must be a power of 2
    fixatnNoiseTexture = np.round( np.random.rand(nearestPowerOfTwo,nearestPowerOfTwo) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation
    fixation= visual.GratingStim(myWin,pos=(0,0), tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=autoLogging)
    fixationBlank= visual.GratingStim(myWin,pos=(0,0), tex=-1*fixatnNoiseTexture, colorSpace='rgb',mask='circle',size=fixSizePix,units='pix',autoLog=autoLogging)
else:
    fixation = visual.GratingStim(myWin,tex='none',colorSpace='rgb',color=(.9,.9,.9),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
    fixationBlank= visual.GratingStim(myWin,tex='none',colorSpace='rgb',color=(-1,-1,-1),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
fixationPoint = visual.GratingStim(myWin,colorSpace='rgb',color=(1,1,1),mask='circle',units='pix',size=2,autoLog=autoLogging) #put a point in the center

#range for grey stimulus
greyShades = [0.2, 1]

# Create a circle stimulus
circle = visual.Circle(
    win=myWin,
    radius=50,  # Radius 
    edges=128,  # Number of edges to approximate the circle
    #lineColor='black'  # Line color
)
respCircle = visual.Circle(
    win=myWin,
    radius=50,  # Radius 
    edges=128,  # Number of edges to approximate the circle
    fillColor='blue'  # Fill color
    #lineColor='black'  # Line color
)
minStimDur = 0.5  # Minimum duration
maxStimDur = 1  # Maximum duration

stimDur = np.random.uniform(minStimDur, maxStimDur)
stimDurFrames = int( np.floor(stimDur / (1./refreshRate)) )
speed = 6 #degrees/second
changeRadiusPerFrame = speed*1./refreshRate


respPromptStim = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
acceptTextStim = visual.TextStim(myWin,pos=(0, -.7),colorSpace='rgb',color=(1,1,1),alignHoriz='center', alignVert='center',height=.1,units='norm',autoLog=autoLogging)
acceptTextStim.setText('Hit ENTER to accept. Backspace to edit')
respStim = visual.TextStim(myWin,pos=(0,0),colorSpace='rgb',color=(1,1,0),alignHoriz='center', alignVert='center',height=.16,units='norm',autoLog=autoLogging)
clickSound, badKeySound = stringResponse.setupSoundsForResponse()
requireAcceptance = False

def collectResponse(probe,autopilot,quitExperiment):
    #Handle response, calculate whether correct, ########################################
    respPromptStim.setText('Press J to move probe outward, K to move inwards; use H and L for larger steps')
    #Set probe to have a random initial radius
    probeInitialRadius = np.random.uniform(radiusMin/2,radiusMax+radiusMin/2)
    probe.radius = probeInitialRadius
    trials.addData('probeInitialRadius',probeInitialRadius)

    #Create a loop allowing participant to move a probe to where they thought the stimulus started
    #and then accept or reject the response
    respFinished = False
    if autopilot: #set response to random
        probe.radius = random.uniform(radiusMin,radiusMax)
    respRadius = probe.radius
    minRadius = .01
    maxRadius = 50
    hasResponded = False
    rtClock = core.Clock()
    rtClock.reset()
    while not autopilot and not respFinished and not quitExperiment:
        respPromptStim.draw()
        probe.radius = respRadius
        probe.draw()
        myWin.flip()
        #Check for response
        keys = event.getKeys()
        if len(keys) > 0:
            #Just check first key pressed since last frame
            key = keys[0]
            key = key.upper()
            print(key)
            if hasResponded and key in ['ENTER','RETURN']:
               respFinished = True
            elif key in ['J']:
                respRadius = respRadius - 0.5
                hasResponded = True
            elif key in ['K']:
                respRadius = respRadius + 0.5
                hasResponded = True
            elif key in ['H']:
                respRadius = respRadius - 3
                hasResponded = True
            elif key in ['L']:
                respRadius = respRadius + 3
                hasResponded = True
            elif key in ['ESCAPE']:
                quitExperiment = True
            respRadius = max(minRadius,respRadius) #Don't allow negative respRadius value
            respRadius = min(maxRadius,respRadius)
        psychopy.event.clearEvents() #Clear keyboard and mouse buffer
        #print('After clearing, event.getKeys = ',event.getKeys())
    respTime = rtClock.getTime()
    return respRadius, quitExperiment, respTime

fixatnMinDur = 0.6
fixatnVariableDur = 0.4
        
trialClock = core.Clock()
# run the experiment
ts = list();
trialNum = 0
quitExperiment = False
for thisTrial in trials:  # handler can act like a for loop
    randomGrey = choice(greyShades)
    circle.fillColor= [randomGrey, randomGrey, randomGrey]  # Fill color
    fixatnPeriodFrames = int(   (fixatnMinDur + np.random.rand(1)*fixatnVariableDur)   *refreshRate)  #random interval
    for frame in range(fixatnPeriodFrames):
        if frame % 2:
            fixation.draw()#flicker fixation on and off at framerate to see when skip frame
        else:
            fixationBlank.draw()
        fixationPoint.draw()
        myWin.flip()
    
    #stimulus 
    circle.radius =  thisTrial['circleRadius']
    for L in range(len(ts)):
        ts.remove(ts[0]) #clear ts array, in case that helps avoid memory leak
    t0=trialClock.getTime()       

    for frame in range(stimDurFrames):
        #Determine what frame we are on
        #if useClock: #Don't count on not missing frames. Use actual time.
        #  t = clock.getTime()
        #  n = round(t*refreshRate)
        #else:

        circle.draw()

        #Drawing fixation after stimuli rather than before because gratings don't seem to mask properly, leaving them showing at center 
        if frame % 2:
            fixation.draw()#flicker fixation on and off at framerate to see when skip frame
        else:
            fixationBlank.draw()
        fixationPoint.draw()
        
        circle.radius = circle.radius + thisTrial['direction'] * changeRadiusPerFrame 
        myWin.flip()
        t=trialClock.getTime()-t0;
        ts.append(t);        
    #end of big stimulus loop

    #Collect response
    trialNum += 1  # just for a quick reference

    msg = 'trial %i had position %s in the list (circleRadius=%.1f)'
    print(msg % (trialNum, trials.thisIndex, thisTrial['circleRadius']))

    respRadius, quitExperiment, respTime = collectResponse(respCircle,autopilot,quitExperiment)
    print('quitExperiment=',quitExperiment,'respRadius=',respRadius)
    trials.data.add('responseRadius',respRadius)
    respError = respRadius - thisTrial['circleRadius']
    print('respError=',respError)
    trials.data.add('respError', respError)
    trials.data.add('respTime', respTime)  # add the data to our set
    
    helpersAOH.accelerateComputer(0,process_priority, disable_gc) #turn off stuff that sped everything up. But I don't know if this works.
    #check for timing problems
    interframeIntervs = np.diff(ts)*1000 #difference in time between successive frames, in ms
    idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded longerThanRefreshTolerance of expected duration
    numCasesInterframeLong = len( idxsInterframeLong )
    #Also check for short frames, because MacOS Sonoma etc. have a bug so frame sync blocking doesn't work
    idxsInterframeShort = np.where( interframeIntervs < shortFrameLimit ) [0] #frames shorter than tolerable
    numCasesInterframeShort = len( idxsInterframeShort )
    #Report on any long frames
    if numCasesInterframeLong >0:
       longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         longFramesStr += 'not printing them all because in demo mode'
       else:
           longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
       if longFramesStr != None:
                msg= 'trialnum=' + str(trialNum) + ' ' + longFramesStr
                print(msg, file=logF)
                print(msg)
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                        if idx-1>=0:  flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    #print >>logF, 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) ) 
    #Informally, I noticed that it's only at the beginning of a trial that I see frequent fixation flicker (timing blips), so
    if numCasesInterframeShort >0:
       shortFramesStr =  'ERROR,'+str(numCasesInterframeShort)+' frames were longer than '+str(longFrameLimit)+' ms'
       if demo: 
         shortFramesStr += 'not printing them all because in demo mode'
       else:
           shortFramesStr += ' apparently some screen refreshes were not waited for, interframe durs were:'+\
                    str( np.around(  interframeIntervs[idxsInterframeShort] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeShort)
       if shortFramesStr != None:
                msg= 'trialnum=' + str(trialNum) + ' ' + shortFramesStr
                print(msg, file=logF)
                print(msg)
                if not demo:
                    flankingAlso=list()
                    for idx in idxsInterframeShort: #also print timing of one before and one after long frame
                        if idx-1>=0:  flankingAlso.append(idx-1)
                        else: flankingAlso.append(np.NaN)
                        flankingAlso.append(idx)
                        if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                        else: flankingAlso.append(np.NaN)
                    #print >>logF, 'flankers also='+str( np.around( interframeIntervs[flankingAlso], 1) ) 
    #Informally, I noticed that it's only at the beginning of a trial that I see frequent fixation flicker (timing blips), so

    #separately report num timingBlips after fixation and after target cueing, because it dont' really matter earlier
    numLongFramesAfterFixation = len(  np.where( idxsInterframeLong > fixatnPeriodFrames )[0] )
    print('numLongFramesAfterFixation=',numLongFramesAfterFixation)
    trials.data.add('numLongFramesAfterFixation',numLongFramesAfterFixation)
    numShortFramesAfterFixation = len(  np.where( idxsInterframeShort > fixatnPeriodFrames )[0] )
    print('numShortFramesAfterFixation=',numShortFramesAfterFixation)
    trials.data.add('numShortFramesAfterFixation',numShortFramesAfterFixation)

    trials.addData('greyShade', randomGrey) # Record the shade of grey used
    #end timing check

    if quitExperiment:
        break

# After the experiment, print a new line
print('\n')

# Write summary data to a text file ...
trials.saveAsText(fileName=datafileName+'summary')

# ... or an xlsx file (which supports sheets)
trials.saveAsExcel(fileName=datafileName+'.xls')

# Save a copy of the whole TrialHandler object, which can be reloaded later to
# re-create the experiment.
trials.saveAsPickle(fileName=datafileName)

# Wide format is useful for analysis with R or SPSS.
trialHandlerDatafilename = datafileName+'wide'
df = trials.saveAsWideText(trialHandlerDatafilename,delim='\t')

#End of experiment
if quitFinder and ('Darwin' in platform.system()): #If turned Finder (MacOS) off, now turn Finder back on.
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)
print('Got to the end of the program and now quitting normally.')
core.quit()