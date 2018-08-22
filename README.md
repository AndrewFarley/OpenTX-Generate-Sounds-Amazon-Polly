# OpenTX Generate Sounds with Amazon Polly

**Found at:** https://github.com/AndrewFarley/OpenTX-Generate-Sounds-Amazon-Polly
## Author
* Farley - farley _at_ **neonsurge** _dot_ com

## Purpose
1. To generate much nicer sounding audio feedback files for OpenTX transmitters.
1. To allow users to customize the sounds easily on their handset

## How does it do this?
1. This uses a Python script that shouldn't require any additional installation or configuration to run on supported operating systems (OS-X only currently).  This script operates in two modes...
    1. Single-use mode, generating a single mp3/wav file.  Good for making custom sounds.
    2. CSV-parsing mode, parsing the OpenTX language .csv file and generating files with the contents and folder structure defined therein
1. The Python script leverages [Amazon Polly](https://aws.amazon.com/polly/), an amazing text-to-speech engine from Amazon with an API.
1. Finally, we leverage a tool on supported operating systems to convert to a WAV file of the specific format that OpenTX expects (16-bit 32000hz WAV).

## Prerequisites

- Python 2.x (already on nearly every OS-X/Linux machine ever)
- [Create a free AWS account (not sponsored or anything)](https://aws.amazon.com/free/)
- [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/installing.html)
- [Setup your AWS CLI credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) (aka, `aws configure`)

## Usage

First, clone this repository with git...
```bash
git clone https://github.com/AndrewFarley/OpenTX-Generate-Sounds-Amazon-Polly.git
cd OpenTX-Generate-Sounds-Amazon-Polly
```

Check out its help/manpage with...
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


# Generate a single sound with this command
./generate_sounds.py -s "Lets go fly"
# If it succeeded you will see this output and in this folder you've
# got a sample.wav file now that you can put right onto your OpenTX compatible device

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

Then choose a voice

```
./generate_sounds.py -v Nicole -o Nicole --csv ./en-US-taranis.csv
./generate_sounds.py -v Geraint -o Geraint --csv ./en-US-taranis.csv
```


# Deploy it with...
serverless deploy

# Run it manually with...
serverless invoke --function daily_snapshot --log
```

Now go tag your instances (manually, or automatically if you have an automated infrastructure like [Terraform](https://www.terraform.io/) or [CloudFormation](https://aws.amazon.com/cloudformation/)) with the Key "Backup" (with any value) which will trigger this script to back that instance up.

If you'd like to specify the number of days to retain backups, set the key "Retention" with a numeric value.  If you do not specify this, by default keeps the AMIs for 7 days.

![ec2 image tag example](./snapshot.png)

After tagging some servers, try to run it manually again and check the output to see if it detected your server. To make sure your tag works, go run the lambda yourself manually and check the log output.  If you tagged some instances and it ran successfully, your output will look something like this...

```bash
bash-3.2$ serverless invoke --function daily_snapshot --log
--------------------------------------------------------------------
Scanning region: eu-central-1
Scanning for instances with tags (backup,Backup)
  Found 2 instances to backup...
  Instance: i-00001111222233334
      Name: jenkins-build-server
      Time: 7 days
       AMI: ami-00112233445566778
  Instance: i-55556666777788889
      Name: primary-webserver
      Time: 7 days
       AMI: ami-11223344556677889
Scanning for AMIs with tags (AWSAutomatedDailySnapshots)
  Found AMI to consider: ami-008e6cb79f78f1469
           Delete After: 06-12-2018
This item is too new, skipping...
Scanning region: eu-west-1
Scanning for instances with tags (backup,Backup)
  Found 0 instances to backup...
Scanning for AMIs with tags (AWSAutomatedDailySnapshots)
Scanning region: eu-west-2
```

### That's IT!
Now every day, once a day this lambda will run and automatically make no-downtime snapshots of your servers.

## Updating
If you'd like to tweak this function it's very easy to do without ever having to edit code or re-deploy it.  Simply edit the environment variables of the Lambda.  If you didn't change the region this deploys to, you should be able to [CLICK HERE](https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/functions/daily-instance-snapshot-dev-daily_snapshot) and simply update any of the environment variables in the Lambda and hit save.  Seen below...

![lambda update env variable](./snapshot2.png)

 * **DEFAULT_RETENTION_TIME** is the default number of days that it will keep backups for
 * **DRY_RUN** you only need to set to true briefly, if you want to test-run this script to see what it would do.  Warning: if you set this to true, make sure you un-set it, otherwise your lambda won't do anything.
 * **KEY_TO_TAG_ON** is the tag that this script will set on any AMI it creates.  This is what we will scan for to cleanup AMIs afterwards.  WARNING: Changing this value will cause any previous AMIs this script made to suddenly be hidden to this script, so you will need to delete yourself.
 * **LIMIT_TO_REGIONS** helps to speed this script up a lot by not wasting time scanning regions you aren't actually using.  So, if you'd like this script to speed up then set the this to the regions (comma-delimited) you wish to only scan.  Eg: us-west-1,eu-west-1.

## Scheduling Backups At Specific Start Times
- ref: [Schedule Expressions Using Rate or Cron](https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html)
* If you wish to schedule the time for your AMI backups, simply edit the serverless.yml `rate` and use the cron syntax as follows:
I.e.: Invoke our Lambda automated AMI/snapshot backups function start time for 09:00am (UTC) everyday (which is currently 2AM PST with DLST in effect):
    ```
    egrep -A 1 'rate:' ./serverless.yml
    #rate: rate(1 day) # this is the default value
    rate: cron(0 09 * * ? *)
    enabled: true
    ```

## Validate Our AMIs with AWS CLI Commands and Filtering
* The below example command shows the desired metadata from all of all our automated AMI's created with the tag and key value pair: Backup / true
    ```
    aws ec2 describe-images --owners self --filters "Name=tag:Backup,Values=true"  \
    --query 'Images[ * ].{ID:ImageId, ImgName:Name, Owner:OwnerId, Tag:Description, CreationDate:CreationDate}' |  jq .
    [
    {
        "ID": "ami-123c8a43",
        "ImgName": "myserver.mydomain.com-backup-2018-07-02-09-00-34",
        "Owner": "012345678901",
        "Tag": "Automatic Daily Backup of myserver.mydomain.com from i-098765b1a132aa1b",
        "CreationDate": "2018-07-02T09:00:34.000Z"
    },
     ...
    ```

## Removal

Simple remove with the serverless remove command.  Please keep in mind any AMIs this script may have created will still be in place, you will need to delete those yourself.

```
serverless remove
```


## Changelog / Major Recent Features

* June 6, 2018  - Initial public release
* June 21, 2018 - Moved configuration to env variables, bugfix, more exception handling


## Support, Feedback & Questions

Please feel free to file Github bugs if you find any.  It's probably easier if you fork my repo to make your own modifications detailed above and commit them.  If you make any fixed/changes that are awesome, please send me pull requests or patches.

If you have any questions/problems beyond that, feel free to email me at one of the emails in [author](#author) above.