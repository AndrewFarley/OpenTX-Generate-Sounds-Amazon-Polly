#!/usr/bin/env python2

# Libraries and imports...
import csv
import sys
import boto3
import os
import platform
import subprocess
polly = boto3.client('polly')

# CLI Args and options
from optparse import OptionParser
usage = '  \n\
    %prog --single "Lets go fly" \n\
or \n\
    %prog --csv /Volumes/NO-NAME/SOUNDS/en/SYSTEM/en-US-taranis.csv \n\
'
parser = OptionParser(usage=usage)
parser.add_option("-a", "--autoplay",
                action="store_true",
                dest="autoplay",
                default=False,
                help="Automatically play sounds generated (default True for single, default False for csv, add this arg to switch the default state)")
parser.add_option("-v", "--voice",
                dest="voice",
                help="The voice ID to use, default Joanna;  See --list",
                metavar="id",
                default="Joanna")
parser.add_option("-l", "--list",
                action="store_true",
                dest="list",
                default=False,
                help="List the voices available and exits")
parser.add_option("-s", "--single",
                dest="single",
                help="A single sound file to generate, you can use any language and full UTF-8 characters",
                metavar="phrase",
                default="The quick brown fox jumps over the lazy dog")
parser.add_option("-o", "--output",
                dest="output",
                help="The filename to output to when doing a single sound output, do not put .wav or .mp3 here, or the folder name to output when parsing a csv",
                metavar="file_or_folder_name",
                default="sample")
parser.add_option("--csv",
                dest="csvfile",
                help="The file path to a .csv file to load a list of files to generate (; delimited, not comma-delimited).  The format we are expecting is... \n FOLDERPATH;FILENAME;PHRASE",
                metavar="filepath",
                default="")
parser.add_option("-f", "--format",
                dest="format",
                help="The format to generate",
                metavar="format",
                default="wav")
# Parse CLI Arguments
(options, args) = parser.parse_args()

# Helper to left-justify output easily
def ljustprint(str,just=14):
    sys.stdout.write(str.ljust(just))

# Helper to convert a mp3 file to a wave
def convert_to_wave(filepath, output_filepath):
    if platform.system() == 'Darwin':
        try:
            print("Attempting to convert the sound file to WAVE via afconvert on OS-X...")
            if subprocess.call('afconvert -f WAVE -d LEI16@32000 {} {}'.format(filepath, output_filepath), shell=True) == 0:
                return True
            else:
                print("Unknown error while converting wave file, please report a bug")
                exit(1)
        except:
            print("Sorry, an error occurred while trying to convert this on your computer, see error below and report a bug if you can/want")
            raise
    # TODO: Add other OS-es?
    else:
        print("Sorry, this script only supports OS-X to convert the file to a wave format...")
        exit(1)

# Play the file if possible...
def play_if_possible(file):
    if platform.system() == 'Darwin':
        try:
            print("Attempting to play the sound file since we are on OS-X...")
            if subprocess.call('afplay {}'.format(file), shell=True) == 0:
                return True
        except:
            print("Sorry, an error occurred while trying to auto-play this on your computer.")
    # TODO: Add other OS-es?
    else:
        print("Sorry, this script only supports OS-X to auto-play the sound, skipping auto-play...")
    return False

# Print our available polly voices to the screen
def describe_available_polly_voices():
    
    # Retrieve our data
    response = polly.describe_voices()

    # Printing the headers
    print('-' * 51)
    ljustprint("| Sex", 6)
    ljustprint("| Voice ID")
    ljustprint("| Language", 30)
    print("|")
    print('-' * 51)

    # Print the voices in a sexy CLI table, sorted by the language
    for voice in sorted(response['Voices'], key=lambda k: k['LanguageName']) :
        ljustprint("|  {}".format("M" if voice['Gender'] == "Male" else "F"), 6)
        ljustprint("| {}".format(voice['Id']))
        ljustprint("| {}".format(voice['LanguageName']), 30)
        print("|")

    # Footer
    print('-' * 51)

# Helper to generate a mp3 file for a voice and phrase
def generate_mp3_from_polly(voice, filename, phrase):
    # Generate our sound file from Amazon
    try:
        response = polly.synthesize_speech(VoiceId=voice,
                                           OutputFormat='mp3', 
                                           Text = phrase)
    except:
        print('-' * 51)
        print("Error while trying to synthesize speech on Amazon")
        print("Please check that you have CLI credentials setup for")
        print("amazon (via: aws cli configure)")
        print('-' * 51)
        raise
    
    # Save to a file... 
    file = open(filename, 'w')
    file.write(response['AudioStream'].read())
    file.close()
    print("Generated sample to {}".format(filename))

#################################
# MAIN LOGIC BEGINS HERE
#################################

# If the user requested a list of voices then print it and exit
if options.list:
    describe_available_polly_voices()
    exit(0)

# if the user requested to parse the taranis csv, then lets do it
if options.csvfile:
    # First simple filepath checking
    if not os.path.isfile(options.csvfile):
        print("ERROR: The file does not exist: {}".format(options.csvfile))
        exit(1)
    # Then trying to parse...
    records = []
    try:
        with open(options.csvfile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in csvreader:
                records.append({'path': row[0], 'filename': row[1], 'phrase': row[2]})
    except:
        print("ERROR: Error while processing file, see below...")
        raise

    print("Found {} sounds to create...".format(len(records)))
    for sound in records:
        destination_path = "{}/{}/{}".format(options.output, sound['path'], sound['filename'])
        # Create our sound
        print("Creating phrase '{}' into {}...".format(sound['phrase'], destination_path))
        generate_mp3_from_polly(options.voice, 'temp.mp3', sound['phrase'])
        # Convert it to wave if desired
        if options.format == 'wav':
            convert_to_wave('temp.mp3', 'temp.mp3.wav')
            os.unlink('temp.mp3')
            os.rename('temp.mp3.wav', 'temp.sound')
        else:
            os.rename('temp.mp3', 'temp.sound')
        # Make sure the destination folder(s) exists...
        if not os.path.exists(os.path.dirname(destination_path)):
            try:
                os.makedirs(os.path.dirname(destination_path))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        # Move into destination
        os.rename('temp.sound', destination_path)
        # Play if desired
        if options.autoplay:
            play_if_possible(destination_path)

        print("Created {}".format(destination_path))

    print("Successfully finished processing")
    exit(0)


# if the user requested a single record, then generate it and exit
if options.single:
    # Debug output
    print("Generating sample sound, phrase: ")
    print("  {}".format(options.single))
    
    # Generate mp3 from polly
    mp3_filename = "{}.mp3".format(options.output)
    generate_mp3_from_polly(options.voice, mp3_filename, options.single)
        
    # Play it if possible from the CLI
    if not options.autoplay:
        play_if_possible(mp3_filename)
    
    # Convert to wave if desired
    if options.format == 'wav':
        wav_filename = "{}.wav".format(options.output)
        print("Converting to wave file...")
        convert_to_wave(mp3_filename, wav_filename)
        print("Generated final sample wav to {}".format(wav_filename))

    exit(0)
