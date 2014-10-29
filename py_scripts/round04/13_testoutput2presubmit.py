#!/usr/bin/env python

import sys
import re


#######################################################################################################################
###################### Sentences Processing ###########################################################################
#######################################################################################################################



def procSentenceList(sentenceList):

    # Format of each tuple: 0-phraseId | 1-sentenceId | 2-phraseLen | 3-phrase | 4 - Sentiment | 5 - PTB Phrase
    sortedList = sorted(sentenceList, key=lambda phrs: (phrs[1],phrs[2]))
    treePhrases = []

    lastEle = sortedList[-1]

    strRegex = "(\([0-9]\s[^\(\)]*\))"
    regexObj = re.compile(strRegex)
    sentenceParts = regexObj.split(lastEle[5])

    newSentence = ""

    controle = 0

    while (sentenceParts != None and newSentence.strip() != lastEle[3].strip() and controle < 50 ):
        newSentence = ""

        for part in sentenceParts:

            #Brings just the nodes that are Leafs
            if ( regexObj.search(part) ):

                #Get the label from the Leaf
                reLabel = re.search(r'\([0-9]\s([^\(\)]*)\)',part)
                reSentiment = re.search(r'\(([0-9])\s([^\(\)]*)\)',part)

                if reLabel != None and reSentiment != None:
                    part = reLabel.group(1)
                    newSent = reSentiment.group(1)
                    treePhrases.append( {'phrase':part, 'sentiment':newSent} )
                else:
                    errorMsg = "The phrase %s was not processed because an error in the tree parser. " % str(lastEle[0])
                    sys.stderr.write(errorMsg)

            # Rebuild the phrase replacing the leafs
            newSentence = newSentence + part

        sentenceParts = regexObj.split(newSentence)
        controle = controle + 1

    for i, phraseTup in enumerate(sortedList):
        currTup = phraseTup

        for tPhrase in treePhrases:
            if phraseTup[3].strip().lower() == tPhrase['phrase'].strip().lower():
                if ( int(phraseTup[4]) != int(tPhrase['sentiment']) ):
                    errorMsg = "Updating the sentiment for the phrase %s. \n" % str(phraseTup[0])
                    sys.stderr.write(errorMsg)
                    errorMsg =  "old[%s] new[%s]:\t%s\n" % ( str(phraseTup[4]),
                                                             str(tPhrase['sentiment']),
                                                             str(phraseTup[3])
                    )

                    sys.stderr.write(errorMsg)

                    sortedList[i] = [phraseTup[0],
                                     phraseTup[1],
                                     phraseTup[2],
                                     phraseTup[3],
                                     int(tPhrase['sentiment']),
                                     phraseTup[5]]


    outputList = sorted(sortedList, key=lambda phrs: (phrs[1],phrs[0]))

    for currTup in outputList:
        print "%s\t%s\t%s\t%s\t%s" % (str(currTup[0]),str(currTup[1]),str(currTup[3]),str(currTup[4]),str(currTup[5]))


#######################################################################################################################
###################### M A I N   C O D E ##############################################################################
#######################################################################################################################


global_currSentenceList = []
global_currSentenceId = -1
line_number = 0

next(sys.stdin)
print "PhraseId\tSentenceID\tPhrase\tSentiment"

for line in sys.stdin:
    line_number = line_number +1
    try:
        # Format of input: phraseId\tsentenceId\tphrase\tsentiment
        # strip the line of leading and trailing whitespace,
        # PhraseId	SentenceId	numLeftParts	leftParts	Phrase	Sentiment	numWords	numChars	PTBPhrase

        (phraseId,
         sentenceId,
         isMain,
         numLeftParts,
         leftParts,
         phrase,
         sentiment,
         numWords,
         numChars,
         ptbPhrase) = line.strip().split("\t")

    except:
        # tells Hadoop to count the records we failed to parse
        errorMsg = "reporter:counter:TRAINFILE,SKIPPED_LINES,%s\n" % str(line_number)
        sys.stderr.write(errorMsg)
        continue

    # Process the previous sentence's group of phrase when the sentence ID found is different
    if (int(sentenceId) > global_currSentenceId and global_currSentenceId >= 0):
        procSentenceList ( global_currSentenceList )
        global_currSentenceList = []

    # Format of each tuple: 0-phraseId | 1-sentenceId | 2-phraseLen | 3-phrase | 4 - Sentiment | 5 - PTB Phrase
    global_currSentenceList.append( [int(phraseId), int(sentenceId), len(phrase), phrase,int(sentiment),ptbPhrase]  )
    global_currSentenceId = int(sentenceId)


# Process the last sentence's group of phrase.
procSentenceList ( global_currSentenceList )