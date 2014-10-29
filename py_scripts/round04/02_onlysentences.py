#!/usr/bin/env python

import sys


#######################################################################################################################
###################### M A I N   C O D E ##############################################################################
#######################################################################################################################
# This script will keep only the root sentences and will remove the partial phrases.

global_currSentenceList = []
global_currSentenceId = -1

next(sys.stdin)
for line in sys.stdin:
    try:
        # Format of input: phraseId\tsentenceId\tphrase\tsentiment
        # strip the line of leading and trailing whitespace,
        (phraseId,sentenceId,totalPartsLeft, PartsLeft, phrase, sentiment,wordsCount, charsCount,ptbPhrase) = line.strip().split("\t")
    except:
        sys.stderr.write("SKIPPED_LINES,1\n")
        continue
    
    # Process the previous sentence's group of phrase when the sentence ID found is different
    if (int(sentenceId) > global_currSentenceId and global_currSentenceId >= 0):
        lastEle = sorted(global_currSentenceList, key=lambda phrs: (phrs[1],phrs[2]))[-1]
        print "%s\t%s\t%s" % (str(lastEle[4]),str(lastEle[1]),str(lastEle[3]))
        #print sorted(global_currSentenceList, key=lambda phrs: (phrs[1],phrs[2]))[-1][3]
        
        global_currSentenceList = []
    
    # Format of each tuple: 0-phraseId | 1-sentenceId | 2-phraseLen | 3-ptbPhrase
    global_currSentenceList.append( [int(phraseId), int(sentenceId), int(charsCount), ptbPhrase,int(sentiment)]  )
    global_currSentenceId = int(sentenceId)


# Process the last sentence's group of phrase.

finalEle = sorted(global_currSentenceList, key=lambda phrs: (phrs[1],phrs[2]))[-1]
print "%s\t%s\t%s" % (str(finalEle[4]),str(lastEle[1]),str(finalEle[3]))

#print sorted(global_currSentenceList, key=lambda phrs: (phrs[1],phrs[2]))[-1][3]