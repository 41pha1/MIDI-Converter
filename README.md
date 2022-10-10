
# Youtube Synthesia to MIDI

Are you a penny-pinching upcoming musician like me, that wants to learn how to play the piano without paying a single cent?

Great this repo has you covered!

Simply find any synthesia style video-tutorial on youtube and copy the link.

Now run the script, answer a few simple questions, and there you go! You have a semi-beautiful midi file to further convert to sheet music or anything you'd like.


## Installation

```bash
python -m pip install -r requirements.txt
```


## Example

```
python main.py

Enter YouTube video url: https://www.youtube.com/watch?v=HNPZ6KuJZYk
Enter output Midifile path: test.mid
Enter a starting frame for analizing the video where the keyboard is clearly visible and no keys are pressed: 30
Downloading video...
Done!
Detected 88 keys.
Saved as test.mid !
```

## Result
![alt text](https://github.com/41pha1/MIDI-Converter/blob/main/example-midi.png?width=400)
This is a preview of the generated midi file.

## Disclaimer

I am not responsible for any psychological damage that may occur upon taking a look at the source code.

INSPECT AT YOUR OWN RISK
