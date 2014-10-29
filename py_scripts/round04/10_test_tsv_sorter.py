#!/usr/bin/env python

import sys


#######################################################################################################################
###################### Sentences Processing ###########################################################################
#######################################################################################################################



def procSentenceList(sentenceList):

    # Format of each tuple: 0-phraseId | 1-sentenceId | 2-totalPartsLeft | 3-PartsLeft | 4-phrase | 5-sentiment |
    #                       6-wordsCount | 7-charsCount | 8-ptbPhrase
    sortedList = sorted(sentenceList, key=lambda phrs: (phrs[1],phrs[6],phrs[7]))

    mainPhrase = sortedList[-1]
    print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % ( str(mainPhrase[0]),
                                                   str(mainPhrase[1]),
                                                   "1",
                                                   str(mainPhrase[2]),
                                                   str(mainPhrase[3]),
                                                   str(mainPhrase[4]),
                                                   str(mainPhrase[5]),
                                                   str(mainPhrase[6]),
                                                   str(mainPhrase[7]),
                                                   str(mainPhrase[8])
                                                 )

    for i, phraseTup in enumerate(sortedList):
        if i==(len(sortedList)-1):
            break
        if (len(phraseTup[4].strip()) <= 0 ):
            continue
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % ( str(phraseTup[0]),
                                                       str(phraseTup[1]),
                                                       "0",
                                                       str(phraseTup[2]),
                                                       str(phraseTup[3]),
                                                       str(phraseTup[4]),
                                                       str(phraseTup[5]),
                                                       str(phraseTup[6]),
                                                       str(phraseTup[7]),
                                                       str(phraseTup[8])
                                                    )



#######################################################################################################################
###################### M A I N   C O D E ##############################################################################
#######################################################################################################################


global_currSentenceList = []
global_currSentenceId = -1
line_number = 0

next(sys.stdin)
print "PhraseId\tSentenceId\tIsMain\tPhrase\tSentiment"

for line in sys.stdin:
    line_number = line_number +1
    try:
        # Format of input: phraseId	sentenceId	totalPartsLeft	PartsLeft	phrase	sentiment	wordsCount
        #                   charsCount  ptbPhrase
        # strip the line of leading and trailing whitespace
        lineColumns = line.strip().split("\t")

        (phraseId,sentenceId,totalPartsLeft,partsLeft,phrase,sentiment,wordsCount,charsCount,ptbPhrase) = lineColumns

    except:
        errorMsg = "SKIPPED_LINES, %s\n" % str(line_number)
        sys.stderr.write(errorMsg)
        continue
    
    # Process the previous sentence's group of phrase when the sentence ID found is different
    if (int(sentenceId) > global_currSentenceId and global_currSentenceId >= 0):
        procSentenceList ( global_currSentenceList )
        global_currSentenceList = []
    
    # Format of each tuple: 0-phraseId | 1-sentenceId | 2-totalPartsLeft | 3-PartsLeft | 4-phrase | 5-sentiment |
    #                       6-wordsCount | 7-charsCount | 8-ptbPhrase
    global_currSentenceList.append( [int(phraseId),
                                     int(sentenceId),
                                     int(totalPartsLeft),
                                     partsLeft,
                                     phrase,
                                     int(sentiment),
                                     int(wordsCount),
                                     int(charsCount),
                                     ptbPhrase]  )

    global_currSentenceId = int(sentenceId)


# Process the last sentence's group of phrase.
procSentenceList ( global_currSentenceList )