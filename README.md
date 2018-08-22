# OpenTX Generate Sounds with Amazon Polly

**Found at:** https://github.com/AndrewFarley/OpenTX-Generate-Sounds-Amazon-Polly
## Author
* Farley - farley _at_ **neonsurge** _dot_ com

## Purpose
1. To generate much nicer sounding audio feedback files for OpenTX transmitters.
1. To allow users to customize the sounds easily on their handset

## TL;DR / ADHD / Non-Techies
If you don't want any customization just way better sounding voices you don't need to read any further.  Just go download a pre-created OpenTX sound pack that this code generated in the [Releases Area](https://github.com/AndrewFarley/OpenTX-Generate-Sounds-Amazon-Polly/releases).

## Prerequisites

- Python 2.x (already on nearly every OS-X/Linux machine ever)
- [Create a free AWS account (not sponsored or anything)](https://aws.amazon.com/free/)
- [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)
- [Setup your AWS CLI credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) (aka, `aws configure`)
- Ability to use the Terminal/Console

## Usage

First, clone this repository with git...
```bash
git clone https://github.com/AndrewFarley/OpenTX-Generate-Sounds-Amazon-Polly.git
cd OpenTX-Generate-Sounds-Amazon-Polly
```

Then, go try to generate a single sound with this command
```
./generate_sounds.py -s "Lets go fly"
```
_If it succeeded you will see this output and in this folder you've got a sample.wav file now that you can put right onto your OpenTX compatible device.  NOTE: If this fails, you probably don't have AWS CLI setup properly, see [prerequisites](#prerequisites) above._ 

```
Generating sample sound, phrase: 
  Lets go fly
Generated sample to sample.mp3
Attempting to play the sound file since we are on OS-X...
Converting to wave file...
Attempting to convert the sound file to WAVE via afconvert on OS-X...
Generated final sample wav to sample.wav
```

If you want to change the voice, lets lookup the list of voices...
```
./generate_sounds.py --list
---------------------------------------------------
| Sex | Voice ID    | Language                    |
---------------------------------------------------
|  M  | Russell     | Australian English          |
|  F  | Nicole      | Australian English          |
|  F  | Emma        | British English             |
|  M  | Brian       | British English             |
|  F  | Penelope    | US Spanish                  |
|  M  | Geraint     | Welsh English               |
... MORE CONTINUED HERE WHEN YOU RUN IT ...
```

Then choose a voice, and this time lets choose a file output, but not specify what to say (it'll use a default)

```
./generate_sounds.py -v Geraint -o GeraintSample
```
_If you ran this successfully, you should immediately hear Geraint speaking, telling you about a quick and lazy fox_

Now, lets get to the OpenTX language CSV parsing, you can run the following with a copy of one of the latest en-US files from OpenTX 2.2.2.  You could also specify a file path to your/other OpenTX sound CSVs.

```
./generate_sounds.py --csv ./en-US-taranis.csv
```
This will print out what it does, but it will create a new folder structure in the folder sample, that has all the sound files you requested in that file.  You can basically go remove your existing SOUNDS folder and replace it with what this generates.

Now, if you don't like the voice, choose one of the Voice IDs above, and run it again... here's some samples...
```
./generate_sounds.py -v Nicole -o Nicole --csv ./en-US-taranis.csv
./generate_sounds.py -v Geraint -o Geraint --csv ./en-US-taranis.csv
./generate_sounds.py -v Emma -o Emma --csv ./en-US-taranis.csv
# If you want to hear the sounds as they are created (WARNING: this will take a lot longer to run)
./generate_sounds.py -v Brian -o Brian --csv ./en-US-taranis.csv --autoplay

```
Each of these will make a folder with the Voice's name which will contain the proper folder structure (folder name SOUNDS therein) to copy onto your OpenTX transmitter.

Finally, for more details and options on how to use this script, check out its help/manpage with...
```
./generate_sounds.py --help

Usage:   
    generate_sounds.py --single "Lets go fly" 
or 
    generate_sounds.py --csv ./en-US-taranis.csv 

Options:
  -h, --help            show this help message and exit
  -a, --autoplay        Automatically play sounds generated (default True for
                        single, default False for csv, add this arg to switch
                        the default state)
  -v id, --voice=id     The voice ID to use, default Joanna;  See --list
  -l, --list            List the voices available and exits
  -s phrase, --single=phrase
                        A single sound file to generate, you can use any
                        language and full UTF-8 characters
  -o file_or_folder_name, --output=file_or_folder_name
                        The filename to output to when doing a single sound
                        output, do not put .wav or .mp3 here, or the folder
                        name to output when parsing a csv
  --csv=filepath        The file path to a .csv file to load a list of files
                        to generate (; delimited, not comma-delimited).  The
                        format we are expecting is...
                        FOLDERPATH;FILENAME;PHRASE
  -f format, --format=format
                        The format to generate, wav by default, can also be 
                        set to mp3
```


### That's IT!
Enjoy your customized OpenTX handset, add a custom startup sound (hello.wav), add custom button/toggle sounds to let you know what's going on, amuse your friends, talk crap to your foes at the switch of a button.  Do your worst!  :P

## How does this work?
1. This uses a Python script that shouldn't require any additional installation or configuration to run on supported operating systems (OS-X only currently).  This script operates in two modes...
    1. Single-use mode, generating a single mp3/wav file.  Good for making custom sounds.
    2. CSV-parsing mode, parsing the OpenTX language .csv file and generating files with the contents and folder structure defined therein
1. The Python script leverages [Amazon Polly](https://aws.amazon.com/polly/), an amazing text-to-speech engine from Amazon with an API.
1. Finally, we leverage a tool on supported operating systems to convert to a WAV file of the specific format that OpenTX expects (16-bit 32000hz WAV).


## Changelog / Major Recent Features

* August 22, 2018  - Initial public release


## Support, Feedback & Questions

Please feel free to file Github bugs if you find any.  If you know what you're doing, feel free to send me pull requests also.  Please, if you make any fixes/changes that are awesome, send me pull requests or patches!

If you have any questions/problems beyond that, feel free to email me at one of the emails in [author](#author) above.