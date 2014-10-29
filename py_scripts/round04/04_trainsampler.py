#!/usr/bin/env python

import sys
import re


#######################################################################################################################
###################### Sentiment List Processing ######################################################################
#######################################################################################################################


def procSentList(sentListAux):

  devTestThreshold = int(len(sentListAux) * perctDevTest)
  devThreshold = int(len(sentListAux) * perctDev) + devTestThreshold

  # Format of each tuple: 0-sentiment | 1-sentendeID | 2-ptbPhrase
  for i, phraseTup in enumerate(sentListAux):
    
    if i < devTestThreshold:
        fileDevTest.write("%s\t%s\t%s\n" % (str(phraseTup[0]),str(phraseTup[1]),(phraseTup[2])))
    elif i < devThreshold:
        fileDev.write("%s\t%s\t%s\n" % (str(phraseTup[0]),str(phraseTup[1]),(phraseTup[2])))
    else:
        fileTrain.write("%s\t%s\t%s\n" % (str(phraseTup[0]),str(phraseTup[1]),(phraseTup[2])))

  return None



#######################################################################################################################
###################### M A I N   C O D E ##############################################################################
#######################################################################################################################
# This script get the initial dataset and will split in 2 or 3 different datasets, based in the parameters
# informed.
#
# Can be generated the following files:
#
# train Dataset - The dataset used to train the model
# dev Dataset   - The dataset passed to the training routine to meter the accuracy of the trained model
# test_dev Datase - A dataset to be used after the training to meter the accuracy manually. (**not necessary)
#
#######################################################################################################################



global_currSentList = []
global_currSentVal = -1

file2SampleName = ""
fileTrainName = ""
fileDevName = ""
fileDevTestName = ""
perctDev = 0.0
perctDevTest = 0.0

if (len(sys.argv) > 1):
    file2SampleName = sys.argv[1]
else:
    print "Insufficient args"
    sys.exit()

if (len(sys.argv) > 2):
    perctDev = float(sys.argv[2])
else:
    print "Insufficient args"
    sys.exit()

if (len(sys.argv) > 3):
    perctDevTest = float(sys.argv[3])
else:
    print "Insufficient args"
    sys.exit()

if (len(sys.argv) > 4):
    fileTrainName = sys.argv[4]
else:
    print "Insufficient args"
    sys.exit()

if (len(sys.argv) > 5):
    fileDevName = sys.argv[5]
else:
    print "Insufficient args"
    sys.exit()

if (len(sys.argv) > 6):
    fileDevTestName = sys.argv[6]
else:
    print "Insufficient args"
    sys.exit()

file2Sample = open(file2SampleName, 'r')
fileTrain = open(fileTrainName, 'w')
fileDev = open(fileDevName, 'w')
fileDevTest = open(fileDevTestName, 'w')


for line in file2Sample:
  try:
    (sentiment,sentenceId,ptbPhrase) = line.strip().split("\t")
  except:
    sys.stderr.write("reporter:counter:TRAINFILE,SKIPPED_LINES,1\n")
    continue
  
  # Process the previous setiment's group of phrase when the setiment found is different
  if (int(sentiment) != global_currSentVal and global_currSentVal >=0):
    procSentList(global_currSentList)
    global_currSentList = []

  # Format of each tuple: 0-sentiment | 1-sentendeID | 2-ptbPhrase
  global_currSentList.append( [int(sentiment),int(sentenceId),ptbPhrase]  )
  global_currSentVal = int(sentiment)

# Process the last setiment's group of phrase.
procSentList(global_currSentList)


file2Sample.close()
fileTrain.close()
fileDev.close()


