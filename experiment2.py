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
refreshRate = 80.0
autoLogging = True

monitorname = 'testmonitor'
widthPixRequested= 1024 #1600 #monitor width in pixels
heightPixRequested= 768 #800 #monitor height in pixels
monitorwidth = 40.8 #monitor width in cm
scrn=0 #0 to use main screen, 1 to use external screen connected to computer
fullscr= True #True to use fullscreen, False to not. Timing probably won't be quite right if fullscreen = False
allowGUI = False
viewdist = 65 #cm
bgColor = [0,0,0] # [-1,-1,-1]
useRetina=False


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
dlgBoxTitle = 'Oliver honours 2, and no Mac Retina screen detected'
if has_retina_scrn:
    dlgBoxTitle = 'Oliver honours 2. At least one screen is apparently a Retina screen'
    
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
    refreshMsg1= 'Frames per second measured, ~='+ str( np.round(Hz,1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (np.median(Hzs)-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', close enough to desired val of ' + str( round(refreshRate,1) ) + '(' + str( round(1000/refreshRate,1) ) + 'ms)'
    myWinRes = myWin.size
    myWin.allowGUI =True
myWin.close() #have to close window to show dialog box

demo=False
autopilot=False
trialsPerCondition = 1
subject='William'
session='a'

#############################################################################################
#Create new dialog box, with results of timing test and with experiment parameters to set like subject name and session
dlgLabelsOrdered = list() #new dialog box
session='a'
myDlg = psychopy.gui.Dlg(title="Oliver's onset repulsion experiment", pos=(200,400))
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

##################################################################
#Set up datafile name and log file 
if os.path.isdir('.'+os.sep+'dataRaw2'):
    dataDir='dataRaw2'
else:
    print('"dataRaw2" directory does not exist, so saving data in present working directory')
    dataDir='.'
expname = ''

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
datafileName = dataDir+'/'+subject+ '_' + str(session) + '_' + expname+timeAndDateStr
if not demo: #Create log for timing blips etc.
    logF = logging.LogFile(datafileName+'.log', 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#errors, data and warnings will be sent to this logfile
logging.info(refreshMsg1) #Provide some refresh rate info in log file. Can't do it above where tested because participant name not yet finalized


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

stimList = []
positionMin = 3; positionMax = 15
for circlePosition in range(positionMin, positionMax, 5):
        for direction in [-1,1]:
            stimList.append({'circlePosition': circlePosition, 'direction':direction})

print(stimList)
trials = data.TrialHandler(
    trialList=stimList,
    nReps=1,
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

#enter keys
proceedKeys = ['enter', 'return', 'space']

#range for grey stimulus
greyShades = [0.2, 1]

# Create a circle stimulus
circle = visual.Circle(
    win=myWin,
    radius=0.5,  # Radius 
    edges=128,  # Number of edges to approximate the circle
    #lineColor='black'  # Line color
)
probe = visual.Circle(
    win=myWin,
    radius=0.5,  # Radius 
    edges=128,  # Number of edges to approximate the circle
    fillColor='blue'  # Fill color
    #lineColor='black'  # Line color
)

minStimDur = 0.5  # Minimum duration
maxStimDur = 1  # Maximum duration

stimDur = np.random.uniform(minStimDur, maxStimDur)
stimDurFrames = int( np.floor(stimDur / (1./refreshRate)) )
speed = 6 #degrees/second
changeRadiusPerFrame = speed * (1.0 / refreshRate)

# Define possible positions and directions
positions = [3, -3, 8, -8, 13, -13]  # Degrees away from the center
axes = ['x', 'y']  # Possible axes for the circle to appear
directions = [-1, 1]  # -1 = towards the center, 1 = away from the center

# Defining ranges for response circles


# Function to run the circle movement trials
def collectResponse():
    global quitExperiment  # Use the global quitExperiment flag
    quitExperiment = False
    respFinished = False
    hasResponded = False
    frameCounter = 0
    if axis == 'x':
        if startPos > 0:
            probeInitialPosition = np.random.uniform(3, 15)
        else:
            probeInitialPosition = np.random.uniform(-3, -15)
    elif axis == 'y':
        if startPos > 0:  # Positive y-axis
            probeInitialPosition = np.random.uniform(3, 15)
        else:  # Negative y-axis
            probeInitialPosition = np.random.uniform(-15, -3)
    
    #probe position
    if axis == 'x':
        probe.pos = (probeInitialPosition, 0)  # On the x-axis
    else:
        probe.pos = (0, probeInitialPosition)  # On the y-axis
    
    rtClock = core.Clock()
    rtClock.reset()
    
    while not quitExperiment and not respFinished:
         # Flickering fixation
        if frameCounter % 2:
            fixation.draw()
        else:
            fixationBlank.draw()
        fixationPoint.draw()
        probe.draw()
        myWin.flip()
    # Check for key presses
        keys = event.getKeys()
        if len(keys) > 0:
            #Just check first key pressed since last frame
            key = keys[0]
            key = key.upper()
            print(key)
            if hasResponded and key in ['ENTER','RETURN', 'SPACE']:
               respFinished = True
            elif key in ['A']:
                probe.pos = (probe.pos[0] - 0.5, probe.pos[1])
                hasResponded = True
            elif key in ['D']:
                probe.pos = (probe.pos[0] + 0.5, probe.pos[1])
                hasResponded = True
            elif key in ['W']:
                probe.pos = (probe.pos[0], probe.pos[1] + 0.5)
                hasResponded = True
            elif key in ['S']:
                probe.pos = (probe.pos[0], probe.pos[1] - 0.5)
                hasResponded = True
            elif key in ['ESCAPE']:
                quitExperiment = True
        psychopy.event.clearEvents() #Clear keyboard and mouse buffer
        #print('After clearing, event.getKeys = ',event.getKeys())
    respTime = rtClock.getTime()
    return quitExperiment, respTime

fixatnMinDur = 0.6
fixatnVariableDur = 0.4

trialClock = core.Clock()
# run the experiment
ts = list();
trialNum = 0
quitExperiment = False
frameCounter = 0
for thisTrial in trials:  # handler can act like a for loop
    fixatnPauseFrames = int(0.5 * refreshRate)  # Pause duration (e.g., 0.5 seconds)
    for frame in range(fixatnPauseFrames):
        if frame % 2:
            fixation.draw()  # Flicker fixation
        else:
            fixationBlank.draw()
        fixationPoint.draw()
        myWin.flip()

    fixatnPeriodFrames = int(   (fixatnMinDur + np.random.rand(1)*fixatnVariableDur)   *refreshRate)  #random interval
    for frame in range(fixatnPeriodFrames):
        if frame % 2:
            fixation.draw()#flicker fixation on and off at framerate to see when skip frame
        else:
            fixationBlank.draw()
        fixationPoint.draw()
        myWin.flip()

    circle.position = thisTrial['circlePosition']
    for L in range(len(ts)):
        ts.clear() #clear ts array, in case that helps avoid memory leak
    t0=trialClock.getTime() 

    for frame in range(stimDurFrames):
        startPos = choice(positions)
        axis = choice(axes)
        direction = choice(directions)
        random
        randomGrey = choice(greyShades)

        # Set the initial position of the circle
        if axis == 'x':
            circle.pos = (startPos, 0)  # On the x-axis
        else:
            circle.pos = (0, startPos)  # On the y-axis
        
        circle.fillColor= [randomGrey, randomGrey, randomGrey]  # Fill color

        # Randomize the duration of the movement
        stimDur = np.random.uniform(minStimDur, maxStimDur)
        stimDurFrames = int(np.floor(stimDur / (1. / refreshRate)))

        # Move the circle for the randomized duration
        for frame in range(stimDurFrames):
            # Update the circle's position
            if axis == 'x':
                circle.pos = (circle.pos[0] + direction * changeRadiusPerFrame, 0)
            else:
                circle.pos = (0, circle.pos[1] + direction * changeRadiusPerFrame)
            circle.draw()
            
            if frame % 2:
                fixation.draw()#flicker fixation on and off at framerate to see when skip frame
            else:
                fixationBlank.draw()
            fixationPoint.draw()
            
            myWin.flip()
            t=trialClock.getTime()-t0;
            ts.append(t);
            frameCounter+= 1
        
        trialNum += 1
   
        quitExperiment, respTime = collectResponse()
    
        trials.addData('respTime', respTime)
        trials.addData('circlePosition', thisTrial['circlePosition'])
        trials.addData('axis', axis)
        trials.addData('direction', direction)
        respErrorX = circle.pos[0] - probe.pos[0]
        respErrorY = circle.pos[1] - probe.pos[1]
        trials.addData('respErrorX', respErrorX)
        trials.addData('respErrorY', respErrorY)
        trials.addData('greyShades', randomGrey)
        
        if quitExperiment:
            break
        
        

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
