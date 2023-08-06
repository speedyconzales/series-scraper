#!/bin/bash

SCRIPT_PATH="main.py"
TYPE="anime"
NAME="the-misfit-of-demon-king-academy"
LANGUAGE="Deutsch" # most common: ["Deutsch","Ger-Sub","English"]
NUM_RUNS=1

caffeinate -w $$ & # necessary on a MacBook when running on battery

for ((i=1; i<=NUM_RUNS; i++))
do
    python3 "$SCRIPT_PATH" "$TYPE" "$NAME" "$LANGUAGE" -s 1
done
