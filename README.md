
# Youtube Synthesia to MIDI

Are you a penny-pinching upcoming musician like me, that wants to learn how to play the piano without paying a single cent?

Great this repo has you covered!

Simply find any synthesia style video-tutorial on youtube and copy the link.

Now run the script and there you go! You have a semi-beautiful midi file to further convert to sheet music or anything you'd like.


## Features

- Automatically extracts the key positions
- Only a link to the video is required

## Installation

```bash
python -m pip install -r requirements.txt
```

## Console

```bash
>> python youtube_midify.py --help
Usage: youtube_midify.py <youtube-url / "videofile.mp4"> -o <outputfile = out.mid> -s <start_in_seconds = 0> -e <end_in_seconds = -1> -t <activation_threshold = 30> -k <proportional_keyboard_height_from_top = 0.88>

>> python youtube_midify.py https://youtu.be/HNPZ6KuJZYk
Downloading video...
Detected 88 keys.
Recognized key  39 as middle C.
Saved as out.mid.
```

## Module
```python

from youtube_midify import convert

convert("https://youtu.be/HNPZ6KuJZYk", output = "out.mid", start = 0, end = -1, keyboard_height = 0.85, threshold = 30)

```
## Result
![alt text](https://github.com/41pha1/MIDI-Converter/blob/main/example-midi.png?width=400)
This is a preview of the generated midi file.

## Disclaimer

I am not responsible for any psychological damage that may occur upon taking a look at the source code.

INSPECT AT YOUR OWN RISK
