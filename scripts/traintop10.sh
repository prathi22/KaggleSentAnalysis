#!/bin/bash
# Usage: sh traintop10.sh <step number>

export STANFORD_RUN="/Volumes/BRANDAODISK/Data Science/Kaggle - Desafio/KaggleCode/stanford_run/"

if [[ "$2" && "$2" -gt 10 ]]
then
    export TOP=$2
else
    export TOP=10
fi



if [[ "$1" ]]
then
    export LOG_FILE=$STANFORD_RUN$1
    cat "$LOG_FILE" | grep -e "EVALUATION SUMMARY" -e "Tested ... roots" -A 3 -B 1 | grep "accuracy" | sed ':a;N;$!ba;s/\n  0,2/ 0,2/g' | sed ':a;N;$!ba;s/\n  0,3/ 0,3/g' | sed ':a;N;$!ba;s/\n  0,4/ 0,4/g' | sed 's/ accuracy /\t/g' | sed 's/accuracy/ /g' | sed 's/ //g' | nl | sort -k 2,2nr -k 3,3nr | head -$TOP

else
    echo "Choose a log file name!"
fi
