import sys
import getopt
import cv2
import numpy as np
from mido import Message, MidiFile, MidiTrack, MetaMessage
from pytube import YouTube

__activationThreshold = 30
__whiteThreshold = 150
__minKeyWidth = 3
__blackThreshold = 100
__keyboardHeight = 0.85
__start = 0
__end = -1
__output = "out.mid"
__keyPositions = []
__defaultValues = []
__middleC = 0

def __labelKeys(keyboard):
    cIndex = 0
    cs = []
    global __middleC
    for i in range(len(__defaultValues)-6):
        if(__defaultValues[i]>__whiteThreshold and __defaultValues[i+1]>__whiteThreshold and __defaultValues[i+2]<__blackThreshold and __defaultValues[i+3]>__whiteThreshold and __defaultValues[i+4]<__blackThreshold and __defaultValues[i+5]>__whiteThreshold and __defaultValues[i+6]>__whiteThreshold):
            cs.append(i+1)

    if len(cs) == 0:
        print("Did not detect a valid keyboard at the specified start, check your start time and keyboard height")
        sys.exit(2)
    __middleC = cs[int((len(cs))/2)]
    print("Recognized key ", __middleC, "as middle C.")

def __getPressedKeys(keys):
    pressed = []
    for i in range(len(keys)):
        if(abs(keys[i]-__defaultValues[i])>__activationThreshold):
            pressed.append(1)
        else:
            pressed.append(0)
    return pressed

def __extractKeyPositions(keyboard):
    global __keyPositions, __defaultValues, __whiteThreshold, __blackThreshold, __minKeyWidth

    inWhiteKey = False
    inBlackKey = False
    keyStart = 0
    maxBrightness = max(keyboard)
    minBrightness = min(keyboard)
    __whiteThreshold = minBrightness + (maxBrightness - minBrightness) * 0.6
    __blackThreshold = minBrightness + (maxBrightness - minBrightness) * 0.4

    for i in range(len(keyboard)):
        b = keyboard[i]
        if(b>__whiteThreshold):
            if(not inWhiteKey and not inBlackKey):
                inWhiteKey = True
                keyStart = i
        else:
            if(inWhiteKey):
                inWhiteKey = False
                if(i-keyStart>__minKeyWidth):
                    __keyPositions.append(int((keyStart+i)/2))
                    __defaultValues.append(keyboard[int((keyStart+i)/2)])

        if(b<__blackThreshold):
            if(not inBlackKey and not inWhiteKey):
                inBlackKey = True
                keyStart = i
        else:
            if(inBlackKey):
                inBlackKey = False
                if((i-keyStart)>__minKeyWidth):
                    __keyPositions.append(int((keyStart+i)/2))
                    __defaultValues.append(keyboard[int((keyStart+i)/2)])

    print("Detected", len(__keyPositions), "keys.")

def __print_usage():
    print("Usage: main.py <youtube-url / \"videofile.mp4\"> -o <outputfile = out.mid> -s <start_in_seconds = 0> -e <end_in_seconds = -1> -t <activation_threshold = 30> -k <proportional_keyboard_height_from_top = 0.85>")

def __parse_options(argv):
    global __video, __is_url, __output, __start, __end, __keyboardHeight, __activationThreshold

    if not argv:
        __print_usage()
        sys.exit()
    
    if argv[0].endswith(".mp4"):
        __is_url = False
        __video = argv[0]
    else:
        __video = argv[0]
        __is_url = True

    try:
        opts, args = getopt.getopt(argv[1:],"ho:s:e:k:t:",["help", "output=", "start=", "end=", "keyboard_height=", "threshold="])
    except getopt.GetoptError:
        __print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            __print_usage()
            sys.exit()
        elif opt in ("-o", "--output"):
            __output = arg
        elif opt in ("-s", "--start"):
            __start = (float(arg))
        elif opt in ("-e", "--end"):
            __end = (float(arg))
        elif opt in ("-k", "--keyboard_height"):
            __keyboardHeight = float(arg)
        elif opt in ("-t", "--threshold"):
            __activationThreshold = int(arg)
    

def convert(video, is_url, output = "out.mid", start = 0, end = -1, keyboard_height = 0.85, threshold = 30):
    global __threshold, __keyboardHeight
    __threshold = threshold
    
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    if is_url:
        print("Downloading video...")
        yt = YouTube(video)
        yt.streams.get_by_itag(22).download('videos/')
        inputVideo = 'videos/' + str(yt.title.replace("/", "").replace("'", "").replace("|", "").replace(".", "")) + ".mp4"
    else:
        inputVideo = video
    
    vidcap = cv2.VideoCapture(inputVideo)
    success,image = vidcap.read()
    count = 0
    lastMod = 0

    frame_height, frame_width, _ = image.shape
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    print("Processing video at %dp@%d..." % (frame_height, fps))

    keyboard_height = int(frame_height * keyboard_height)
    startFrame = int(start * fps)
    endFrame = int(end * fps)

    if not success:
        exit("Could not open video: " +  str(inputVideo))

    lastPressed = []

    while success:
        ia = np.asarray(image)
        kb = []

        for x in range(len(ia[0])):
            kb.append( np.mean(ia[keyboard_height][x]) )

        if count == startFrame:
            __extractKeyPositions(kb)
            
            cv2.line(image, (0, keyboard_height), (frame_width, keyboard_height), (0, 255, 0), 2)
            for i in range(len(__keyPositions)):
                cv2.circle(image, (__keyPositions[i], keyboard_height), 7, (255,255,255) if __defaultValues[i] < __whiteThreshold else (0,0,0), -1)
                cv2.circle(image, (__keyPositions[i], keyboard_height), 5, (255,255,255) if __defaultValues[i] > __whiteThreshold else (0,0,0), -1)

            cv2.imwrite("start_frame.jpg", image)
            __labelKeys(kb)

            lastPressed = [0] * len(__keyPositions)

        if(count >= startFrame):
            keys = []

            for i in range(len(__keyPositions)):
                keys.append(kb[__keyPositions[i]])

            pressed = __getPressedKeys(keys)

            for i in range(len(pressed)):
                if not pressed[i] == lastPressed[i]:
                    if(lastMod == 0 and count > fps):
                        lastMod = count-fps
                    if(pressed[i] == 1):
                        track.append(Message('note_on', note = 60 - __middleC + i, velocity=64, time=int((count - lastMod)* fps)))
                        lastMod = count
                    if(pressed[i] == 0):
                        track.append(Message('note_off', note = 60 - __middleC + i, velocity=127, time=int((count - lastMod)* fps)))
                        lastMod = count
            print("Processing frame", count, "...", end="\r")
            lastPressed = pressed
        success,image = vidcap.read()
        count += 1

        if endFrame > 0 and count > endFrame:
            break

    mid.save(output)
    print("Saved as", output, "!               ")

if __name__ == "__main__":
    __parse_options(sys.argv[1:])
    convert(__video, __is_url, __output, __start, __end, __keyboardHeight, __activationThreshold)
    
