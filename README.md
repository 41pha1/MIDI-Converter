
# Youtube Synthesia to MIDI

Are you a penny-pinching upcoming musician like me, that wants to learn how to play the piano without paying a single cent?

Great this repo has you covered!

Simply find any synthesia style video-tutorial on youtube and copy the link.

Now run the script, answer a few simple questions, and there you go! You have a semi-beautiful midi file to further convert to sheet music or anything you'd like.


## Features

- Automatically extracts the key positions
- Only need a link to the video is required

## Installation

```bash
python -m pip install -r requirements.txt
```


## Example

```
python main.py --help
Usage: main.py <youtube-url> -o <outputfile = out.mid> -s <start_in_seconds = 0> -e <end_in_seconds = -1> -t <activation_threshold = 30> -k <proportional_keyboard_height_from_top = 0.88>

python main.py https://youtu.be/HNPZ6KuJZYk

Downloading video...
Detected 88 keys.
Saved as out.mid !
```

## Result
![alt text](https://github.com/41pha1/MIDI-Converter/blob/main/example-midi.png?width=400)
This is a preview of the generated midi file.

## Disclaimer

I am not responsible for any psychological damage that may occur upon taking a look at the source code.

INSPECT AT YOUR OWN RISK
