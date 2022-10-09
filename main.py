import cv2
import numpy as np
import struct
from mido import Message, MidiFile, MidiTrack
from pytube import YouTube
from mido import MetaMessage


activationThreshold = 15
whiteThreshold = 150
minKeyWidth = 3
blackThreshold = 100
downloadVideo = True
if downloadVideo:
    url = str(input("Enter YouTube video url: "))
else:
    inputVideo = str(input("Enter input Videofile path: "))
output = str(input("Enter output Midifile path: "))
keyboardHeight = int(input("Enter keyboard distance from the top in pixels (default = 650): "))
startFrame = int(input("Enter a starting frame for analizing the video where the keyboard is clearly visible and no keys are pressed: "))

keyPositions = []
defaultValues = []
keyLabels = []
middleC = 0

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

    middleC = int((cIndex+lastC)/2)

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
                    keyPositions.append(int((keyStart+i)/2))
                    defaultValues.append(keyboard[int((keyStart+i)/2)])

        if(b<blackThreshold):
            if(not inBlackKey and not inWhiteKey):
                inBlackKey = True
                keyStart = i
        else:
            if(inBlackKey):
                inBlackKey = False
                if((i-keyStart)>minKeyWidth):
                    keyPositions.append(int((keyStart+i)/2))
                    defaultValues.append(keyboard[int((keyStart+i)/2)])

    print("Detected", len(keyPositions), "keys.")


    

if __name__ == "__main__":
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    #MetaMessage('set_tempo', tempo = 30)

    if(downloadVideo):
        print("Downloading video...")
        yt = YouTube(url)
        yt.streams.get_by_itag(22).download('videos/')
        inputVideo = 'videos/' + str(yt.title.replace("/", "").replace("'", "")) + ".mp4"
        print("Done!")
    
    vidcap = cv2.VideoCapture(inputVideo)
    success,image = vidcap.read()
    count = 0
    lastMod = 0

    if not success:
        exit("Could not open video: " +  str(inputVideo))

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
                    if(lastMod == 0 and count > 30):
                        lastMod = count-30
                    if(pressed[i] == 1):
                        track.append(Message('note_on', note = 66 - middleC + i, velocity=64, time=(count - lastMod)*30))
                        lastMod = count
                    if(pressed[i] == 0):
                        track.append(Message('note_off', note = 66 - middleC + i, velocity=127, time=(count - lastMod)*30))
                        lastMod = count
            print("Processing frame", count, "...", end="\r")
            lastPressed = pressed
        success,image = vidcap.read()
        count += 1


    mid.save(output)
    print("Saved as", output, "!               ")
