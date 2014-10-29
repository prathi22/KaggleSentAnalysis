#!/bin/bash
# Usage: sh step.sh <step number>

export PATH_KAGGLE_ROOT=../..
export PYTHON_RND_PATH=$PATH_KAGGLE_ROOT/py_scripts/round04
export DATA_RND_PATH=$PATH_KAGGLE_ROOT/data/round04

export STANFORD_LIB=stanford_classpath3_4

# The best model that I got during the tests was this one:
export SENTIMENT_MODEL=rntn_flat_20141010_a-0123-80,47.ser.gz

if [[ "$2" ]]
then
    export SENTIMENT_MODEL=$2
fi

########################################################################################################################
#Pre-Train
########################################################################################################################

if [ "$1" -eq 1 ]; then
    mkdir DATA_RND_PATH
    cat $PATH_KAGGLE_ROOT/data/train.tsv | $PYTHON_RND_PATH/01_tsv2ptb.py > $DATA_RND_PATH/train_remounted.tsv

elif [ "$1" -eq 2 ]; then
    cat $DATA_RND_PATH/train_remounted.tsv | $PYTHON_RND_PATH/02_onlysentences.py > $DATA_RND_PATH/train_full_2sample.tsv

elif [ "$1" -eq 3 ]; then
    cat $DATA_RND_PATH/train_full_2sample.tsv | sort -t $'\t' -k 1,1 > $DATA_RND_PATH/train_full_2sample_orderd.tsv

elif [ "$1" -eq 4 ]; then
    python $PYTHON_RND_PATH/trainsampler.py $DATA_RND_PATH/train_full_2sample_orderd.tsv 0.082 0.0 $DATA_RND_PATH/sample_train_09.tsv $DATA_RND_PATH/sample_dev_09.tsv $DATA_RND_PATH/sample_test_dev_09.tsv

elif [ "$1" -eq 5 ]; then
    cat $DATA_RND_PATH/sample_train_09.tsv | sort -t $'\t' -k 2,2 | cut -f 3 > $DATA_RND_PATH/pre_train_09.ptb

elif [ "$1" -eq 6 ]; then
    cat $DATA_RND_PATH/sample_dev_09.tsv | sort -t $'\t' -k 2,2 | cut -f 3 > $DATA_RND_PATH/pre_dev_09.ptb

elif [ "$1" -eq 7 ]; then
    java -mx2g -cp "$PATH_KAGGLE_ROOT/stanford_classpath3_4/*:$PATH_KAGGLE_ROOT/java_bin/" br.com.dialect.sentiment.round04.SentimentTreeValidator -trainPath $DATA_RND_PATH/pre_train_09.ptb -devPath $DATA_RND_PATH/pre_dev_09.ptb -prefix pre_

########################################################################################################################
#Train
########################################################################################################################

elif [ "$1" -eq 8 ]; then
    $PATH_KAGGLE_ROOT/stanford_run
    java -mx12g -cp "$PATH_KAGGLE_ROOT/stanford_classpath3_4/*:$PATH_KAGGLE_ROOT/java_bin/" edu.stanford.nlp.sentiment.SentimentTraining -numHid 25 -batchSize 40 -debugOutputEpochs 1 -maxTrainTimeSeconds 345600 -trainPath $DATA_RND_PATH/train_09.ptb -devPath $DATA_RND_PATH/dev_09.ptb -train -model $PATH_KAGGLE_ROOT/stanford_run/rntn_flat_20141010_a.ser.gz > $PATH_KAGGLE_ROOT/stanford_run/rntn_flat_20141010_a.log 2>&1 &

########################################################################################################################
# PRE - Test
########################################################################################################################

elif [ "$1" -eq 9 ]; then
    cat $PATH_KAGGLE_ROOT/data/test.tsv | $PYTHON_RND_PATH/01_tsv2ptb.py > $DATA_RND_PATH/pre_test_ptb.tsv

elif [ "$1" -eq 10 ]; then
    cat $DATA_RND_PATH/pre_test_ptb.tsv | $PYTHON_RND_PATH/10_test_tsv_sorter.py > $DATA_RND_PATH/pre_test_submit.tsv


########################################################################################################################
# Test
########################################################################################################################

elif [ "$1" -eq 11 ]; then
    java -mx2g -cp "$PATH_KAGGLE_ROOT/stanford_classpath3_4/*:$PATH_KAGGLE_ROOT/java_bin/" br.com.dialect.sentiment.round04.SentimentTreeValidator -sentimentModel $PATH_KAGGLE_ROOT/stanford_run/$SENTIMENT_MODEL -testPath $DATA_RND_PATH/pre_test_submit.tsv -prefix pre_

########################################################################################################################
# POST - Test (Mode01)
########################################################################################################################

elif [ "$1" -eq 12 ]; then
    cat $DATA_RND_PATH/test_submit.tsv | cut -f 1,7 | tr '\t' ',' > $PATH_KAGGLE_ROOT/data/submission20141009_b1.csv


########################################################################################################################
# POST - Test (Mode02)
########################################################################################################################

elif [ "$1" -eq 13 ]; then
    cat $DATA_RND_PATH/test_submit.tsv | $PYTHON_RND_PATH/13_testoutput2presubmit.py > $DATA_RND_PATH/presubmit.tsv

elif [ "$1" -eq 14 ]; then
    cat $DATA_RND_PATH/presubmit.tsv | cut -f 1,4 | tr '\t' ',' > $PATH_KAGGLE_ROOT/data/submission20141008_f.csv

########################################################################################################################
# no selection
########################################################################################################################

else
    echo "Choose a Step in the range [1 - 14]!"
    echo $PATH_KAGGLE_ROOT
    echo "$PATH_KAGGLE_ROOT/stanford_classpath3_4/*:$PATH_KAGGLE_ROOT/java_bin/"
fi