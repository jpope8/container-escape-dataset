#!/bin/bash
for (( c=1; c<=16; c++ ))
do
   echo "Loop $c times"
   sleep 20
   python experiment.py 10 A
   sleep 20
   python experiment.py 10 B
   sleep 20
   python experiment.py 10 Z
done
