#!/usr/bin/env bash
./generate_sounds.py --list | grep -i english | awk '{ print $4 }' | while read line ; do
   ./generate_sounds.py -v $line -o $line --csv ./en-US-taranis.csv
   tar -czf $line.tar.gz $line
   echo "Created $line.tar.gz"
done
