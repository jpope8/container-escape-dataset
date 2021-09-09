#!/bin/bash
for (( c=1; c<=16; c++ ))
do
   echo "Loop $c times"
   sleep 20
   python3 experiment.py 10 /storage/logs A
   sleep 20
   python3 experiment.py 10 /storage/logs B
   sleep 20
   python3 experiment.py 10 /storage/logs Z
done
