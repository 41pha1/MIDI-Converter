import sys
import getopt
import cv2
import numpy as np
from mido import Message, MidiFile, MidiTrack, MetaMessage
from pytube import YouTube

activationThreshold = 30
whiteThreshold = 150
minKeyWidth = 3
blackThreshold = 100
keyboardHeight = 640
startFrame = 0
endFrame = -1
output = "out.mid"
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

    if len(keyPositions) < 10:
        print("Did not detect a valid keyboard at the specified start, check your start time and keyboard height")
    print("Detected", len(keyPositions), "keys.")

def print_usage():
    print("Usage: main.py <youtube-url> -o <outputfile = out.mid> -s <start_in_seconds = 0> -e <end_in_seconds = -1> -t <activation_threshold = 30> -k <proportional_keyboard_height_from_top = 0.88>")

def parse_options(argv):
    global url, output, startFrame, endFrame, keyboardHeight, activationThreshold

    if not argv:
        print_usage()
        sys.exit()
    url = argv[0]

    try:
        opts, args = getopt.getopt(argv[1:],"ho:s:e:k:t:",["help", "output=", "start=", "end=", "keyboard_height=", "threshold="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
            sys.exit()
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-s", "--start"):
            startFrame = int(float(arg) * 30)
        elif opt in ("-e", "--end"):
            endFrame = int(float(arg) * 30)
        elif opt in ("-k", "--keyboard_height"):
            keyboardHeight = int(float(arg) * 720)
        elif opt in ("-t", "--threshold"):
            activationThreshold = int(arg)
    

if __name__ == "__main__":
    parse_options(sys.argv[1:])

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    print("Downloading video...")
    yt = YouTube(url)
    yt.streams.get_by_itag(22).download('videos/')
    inputVideo = 'videos/' + str(yt.title.replace("/", "").replace("'", "")) + ".mp4"
    
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

        if not endFrame == -1 and count > endFrame:
            break

    mid.save(output)
    print("Saved as", output, "!               ")
