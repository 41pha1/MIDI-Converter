import cv2
import numpy as np
import struct
from pytube import YouTube
import matplotlib.pyplot as plt


activationThreshold = 15
whiteThreshold = 150
minKeyWidth = 3
blackThreshold = 100
downloadVideo = False
inputVideo = str(raw_input("Enter input Videofile name: "))
output = str(raw_input("Enter input Midifile name: "))
keyboardHeight = int(raw_input("Enter keyboard distance from the top in pixels (default = 650): "))
startFrame = int(raw_input("Enter start a starting frame for analizing the video"))

keyPositions = []
defaultValues = []
keyLabels = []
middleC = 0

midiFile = []
trackLengthIndex = 0

def addMidiHeader(fps):
    midiFile.append(ord('M'))
    midiFile.append(ord('T'))
    midiFile.append(ord('h'))
    midiFile.append(ord('d'))
    midiFile.append(0)
    midiFile.append(0)
    midiFile.append(0)
    midiFile.append(6)
    midiFile.append(0)
    midiFile.append(1)
    midiFile.append(0)
    midiFile.append(1)
    midiFile.append(0)
    midiFile.append(fps)

def beginTrack():
    global trackLengthIndex
    midiFile.append(ord('M'))
    midiFile.append(ord('T'))
    midiFile.append(ord('r'))
    midiFile.append(ord('k'))
    midiFile.append(0)
    midiFile.append(0)
    midiFile.append(0)
    midiFile.append(0)
    trackLengthIndex = len(midiFile)-1

def endTrack():
    midiFile.append(0)
    midiFile.append(0xFF)
    midiFile.append(0x2F)
    midiFile.append(0)
    length = (len(midiFile)-trackLengthIndex)-1
    midiFile[trackLengthIndex-3] = int(length / 0xFF0000)
    midiFile[trackLengthIndex-2] = int(length / 0xFF00) % 0xFF00000
    midiFile[trackLengthIndex-1] = int(length / 0xFF) % 0xFF00
    midiFile[trackLengthIndex] = int(length) % 0xFF

def turnNoteOn(dTime, channel, note, speed):
    midiFile.append(dTime%128)
    midiFile.append(0x90 + channel)
    midiFile.append(note)
    midiFile.append(speed)

def turnNoteOff(dTime, channel, note):
    midiFile.append(dTime%128)
    midiFile.append(0x80 + channel)
    midiFile.append(note)
    midiFile.append(0)

def labelKeys(keyboard):
    cIndex = 0
    global middleC
    for i in range(len(defaultValues)):
        if(defaultValues[i]>whiteThreshold and defaultValues[i+1]>whiteThreshold and defaultValues[i+2]<blackThreshold and defaultValues[i+3]>whiteThreshold and defaultValues[i+4]<blackThreshold and defaultValues[i+5]>whiteThreshold and defaultValues[i+6]>whiteThreshold):
            cIndex = i+1
            break

    lastC = 0
    for i in range(len(defaultValues)):
        label = (120+i-cIndex) % 12
        keyLabels.append(label)
        if label == 0:
            lastC = i

    middleC = (cIndex+lastC)/2

def getPressedKeys(keys):
    pressed = []
    for i in range(len(keys)):
        if(abs(keys[i]-defaultValues[i])>activationThreshold):
            pressed.append(1)
        else:
            pressed.append(0)
    return pressed

def extractKeyPositions(keyboard):
    inWhiteKey = False
    inBlackKey = False
    keyStart = 0
    for i in range(len(keyboard)):
        b = keyboard[i]
        if(b>whiteThreshold):
            if(not inWhiteKey and not inBlackKey):
                inWhiteKey = True
                keyStart = i
        else:
            if(inWhiteKey):
                inWhiteKey = False
                if(i-keyStart>minKeyWidth):
                    keyPositions.append((keyStart+i)/2)
                    defaultValues.append(keyboard[(keyStart+i)/2])

        if(b<blackThreshold):
            if(not inBlackKey and not inWhiteKey):
                inBlackKey = True
                keyStart = i
        else:
            if(inBlackKey):
                inBlackKey = False
                if((i-keyStart)>minKeyWidth):
                    keyPositions.append((keyStart+i)/2)
                    defaultValues.append(keyboard[(keyStart+i)/2])

    print(len(keyPositions))
    plt.plot(keyboard)
    plt.bar(keyPositions, 255)
    plt.pause(5.)
    plt.clf()

if(downloadVideo):
    YouTube(url).streams.first().download('videos/')


addMidiHeader(15)
beginTrack()

vidcap = cv2.VideoCapture(inputVideo)
success,image = vidcap.read()
count = 0
success = True
lastMod = 0

lastPressed = []

while success:
    ia = np.asarray(image)
    kb = []

    for x in range(len(ia[0])):
        kb.append(0)
        for c in range (3):
            kb[x] += ia[keyboardHeight][x][c]
        kb[x] /= 3

    if count == startFrame:
        extractKeyPositions(kb)
        labelKeys(kb)
        lastPressed = [0] * len(keyLabels)

    if(count >= startFrame):
        keys = [];

        for i in range(len(keyPositions)):
            keys.append(kb[keyPositions[i]])

        pressed = getPressedKeys(keys)

        for i in range(len(pressed)):
            if not pressed[i] == lastPressed[i]:
                if(pressed[i] == 1):
                    turnNoteOn(count - lastMod, 0, 0x3C-middleC+i, 0x40)
                    lastMod = count
                if(pressed[i] == 0):
                    turnNoteOff(count - lastMod, 0, 0x3C-middleC+i)
                    lastMod = count
        print(count, middleC)
        #plt.bar(range(len(pressed)), keys)
        #plt.pause(0.005)
        #plt.clf()
        lastPressed = pressed
    success,image = vidcap.read()
    count += 1

endTrack()

outputFile = open(output, "wb")
outputFile.write(struct.pack(str(len(midiFile))+'B', *midiFile))
