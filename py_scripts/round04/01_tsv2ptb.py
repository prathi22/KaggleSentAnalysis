#!/usr/bin/env python

import sys
import re


debug = False
phraseIdDebug = "6790" #1080
sentenceIdDebug = "2518"

#######################################################################################################################
###################### Transform from SentenceList ####################################################################
#######################################################################################################################

def transformPhrase(phraseId,
                    targetPhrase,
                    targetWordsCount,
                    searchList,
                    listInitialIdx,
                    numSearchbParts,
                    isSentenceList):

  currIdx = listInitialIdx
  
  while (currIdx >=0 and numSearchbParts > 0 and int(targetWordsCount) > 1 ):
    
    searchPhrase = searchList[currIdx][2].lower().strip()
    changePhrase = searchList[currIdx][6].lower()

    if ( searchList[currIdx][4] == targetWordsCount ):
        currIdx = currIdx - 1
        continue

    for srchbPart in targetPhrase:

        srchbPartPhrase = srchbPart['partPhrase']
        if( len(srchbPartPhrase.strip()) <= 0 or srchbPart['isPtb'] == True):
          continue

        # If the search phrase has only one character, it will be ignored.
        if( len(searchPhrase.strip()) == 1 and isSentenceList):
            continue

        if( phraseId ==phraseIdDebug and debug ):
            print "[%s][%s][%s]" % (str(srchbPartPhrase),str(searchPhrase),str(currIdx))

        if (srchbPartPhrase.find(searchPhrase) < 0):
            continue

        searchPhraseEscd = re.escape(searchPhrase)

        strRegex = "\\b(%s)\\b" %searchPhraseEscd

        if(re.search(r'[^a-zA-Z0-9\s]', searchPhrase) != None):
            strRegex = "(%s)" % searchPhraseEscd

        regex = re.compile(strRegex)

        newParts = regex.split(srchbPartPhrase)

        srchbPartIdxAdd = targetPhrase.index(srchbPart)
        numSearchbParts = numSearchbParts - 1


        for newPart in newParts:
            if( phraseId ==phraseIdDebug and debug):
                print "==========================[%s]***[%s]***[%s]***[%s]***[%s]========================" % (
                                                    srchbPartPhrase,
                                                    searchPhrase,
                                                    str(len(newParts)),
                                                    newPart,
                                                    str(srchbPartIdxAdd)
                )

            if( phraseId ==phraseIdDebug and debug):
              print newPart
            if ( len(newPart) == 0  ):
                continue

            if ( newPart == " " ):
                targetPhrase.insert( srchbPartIdxAdd, {'partPhrase':newPart,'isPtb':True}  )
                srchbPartIdxAdd = srchbPartIdxAdd + 1
                continue

            if( newPart.lower().strip() == searchPhrase.lower().strip() ):
                if( phraseId ==phraseIdDebug and debug):
                    print "[%s][%s][%s]" % (str(newPart),str(searchPhrase),str(changePhrase))

                targetPhrase.insert( srchbPartIdxAdd, {'partPhrase':changePhrase,'isPtb':True}  )
                srchbPartIdxAdd = srchbPartIdxAdd + 1
            else:
                if( phraseId ==phraseIdDebug and debug):
                    print "[%s][%s][%s]" % (str(newPart),str(searchPhrase),str(srchbPartIdxAdd))

                targetPhrase.insert( srchbPartIdxAdd, {'partPhrase':newPart,'isPtb':False}  )
                srchbPartIdxAdd = srchbPartIdxAdd + 1
                numSearchbParts = numSearchbParts + 1

        targetPhrase.remove(srchbPart)

        if( phraseId ==phraseIdDebug and debug):
            print currIdx

        break
  
    currIdx = currIdx - 1

  return {'targetPhrase':targetPhrase, 'leftParts':numSearchbParts}

#######################################################################################################################
###################### Transform from MemoryBank ######################################################################
#######################################################################################################################

def transformPhraseFromMemory(phraseId, targetPhrase, numSearchbParts):

    atempts = 0

    while (numSearchbParts > 0 and atempts < 5):
        atempts = atempts + 1

        for srchbPart in targetPhrase:

            srchbPartPhrase = srchbPart['partPhrase']

            if( len(srchbPartPhrase.strip()) <= 0 or srchbPart['isPtb'] == True):
                continue

            partFloor =  len(srchbPartPhrase.strip().split(" "))
            currFloor = partFloor+1
            partProcessed = False

            while ( currFloor > 1 ):
                if partProcessed == True:
                    break
                else:
                    currFloor = currFloor - 1

                if( (str(currFloor) in global_memPhrasesList) == True):
                    searchList = global_memPhrasesList[str(currFloor)]
                    #searchListKeys = sorted(searchList.keys(), key=lambda x: (searchList[x][4],searchList[x][5]))
                else:
                    continue

                if currFloor == partFloor:
                    if( phraseId ==phraseIdDebug and debug  ):
                        print "[%s][%s][%s]--->Busca Direta" % (str(srchbPartPhrase),str(currFloor),str(partFloor))

                    if srchbPartPhrase.strip().lower() in searchList:
                        searchKey = srchbPartPhrase.strip().lower()
                    else:
                        continue

                    searchPhrase = searchList[searchKey][2].lower().strip()
                    changePhrase = searchList[searchKey][6].lower()

                    if (searchPhrase == None or len(searchPhrase.strip())<=0 or srchbPartPhrase.find(searchPhrase) < 0):
                        continue

                else:
                    keyFound = False
                    searchMicroPartIdx = 0

                    floorsDiff = (partFloor-currFloor)
                    while searchMicroPartIdx <= floorsDiff:

                        searchKey = ""

                        for mX, microParts in enumerate(srchbPartPhrase.strip().split(" ")):
                            if mX < searchMicroPartIdx:
                                continue

                            searchKey = searchKey + microParts + " "

                            if mX >= (partFloor+searchMicroPartIdx-(floorsDiff+1)):
                                searchKey = searchKey[:-1]
                                break;

                        if( phraseId ==phraseIdDebug and debug  ):
                            print "[%s][%s][%s][%s]--->Busca Por Pisos" % (
                                        str(srchbPartPhrase),
                                        str(searchKey),
                                        str(currFloor),
                                        str(partFloor)
                            )

                        if searchKey.strip().lower() in searchList:
                            keyFound = True
                            break

                        searchMicroPartIdx = searchMicroPartIdx +1

                    if not keyFound:
                        continue

                    searchPhrase = searchList[searchKey][2].lower().strip()
                    changePhrase = searchList[searchKey][6].lower()


                if (searchPhrase == None or len(searchPhrase.strip())<=0 or srchbPartPhrase.find(searchPhrase) < 0):
                    continue

                searchPhraseEscd = re.escape(searchPhrase)

                strRegex = "\\b(%s)\\b" %searchPhraseEscd

                if(re.search(r'[^a-zA-Z0-9\s]', searchPhrase) != None):
                    strRegex = "(%s)" % searchPhraseEscd

                regex = re.compile(strRegex)

                newParts = regex.split(srchbPartPhrase)

                srchbPartIdxAdd = targetPhrase.index(srchbPart)
                numSearchbParts = numSearchbParts - 1

                for newPart in newParts:
                    if( phraseId ==phraseIdDebug and debug):
                        print "==========================[%s]***[%s]***[%s]***[%s]***[%s]========================" % (
                                                            srchbPartPhrase,
                                                            searchPhrase,
                                                            str(len(newParts)),
                                                            newPart,
                                                            str(srchbPartIdxAdd)
                        )

                    if( phraseId ==phraseIdDebug and debug):
                        print newPart
                    if ( len(newPart) == 0  ):
                        continue

                    if ( newPart == " " ):
                        targetPhrase.insert( srchbPartIdxAdd, {'partPhrase':newPart,'isPtb':True}  )
                        srchbPartIdxAdd = srchbPartIdxAdd + 1
                        continue

                    if( newPart.lower().strip() == searchPhrase.lower().strip() ):
                        if( phraseId ==phraseIdDebug and debug):
                            print "[%s][%s][%s]" % (str(newPart),str(searchPhrase),str(changePhrase))

                        targetPhrase.insert( srchbPartIdxAdd, {'partPhrase':changePhrase,'isPtb':True}  )
                        srchbPartIdxAdd = srchbPartIdxAdd + 1
                        partProcessed = True
                    else:
                        if( phraseId ==phraseIdDebug and debug):
                            print "[%s][%s][%s]" % (str(newPart),str(searchPhrase),str(srchbPartIdxAdd))

                        targetPhrase.insert( srchbPartIdxAdd, {'partPhrase':newPart,'isPtb':False}  )
                        srchbPartIdxAdd = srchbPartIdxAdd + 1
                        numSearchbParts = numSearchbParts + 1

                targetPhrase.remove(srchbPart)

    return {'targetPhrase':targetPhrase, 'leftParts':numSearchbParts}



#######################################################################################################################
###################### Sentences Processing ###########################################################################
#######################################################################################################################

# This function will process all the phrases of a specific sentence
def procSentenceList(sentenceListAux):

  # Format of each tuple: 0-phraseId | 1-sentenceId | 2-phrase | 3-sentiment | 4-wordsCount | 5-phraseLen | 6-ptbPhrase
  # Sort the phrases of this sentence by SentenceID, WordsCount, Phrase Lenght
  sortedSentenceList = sorted(sentenceListAux, key=lambda phrs: (phrs[1],phrs[4],phrs[5]))

  #########################################################
  currWordCountFloor = 1
  lastWordCountFloorIdx = 0
  #########################################################

  for i, phraseTup in enumerate(sortedSentenceList):

    searchbPartsLeftStr = "-"
    ptbPhrase = ""
    leftSearchbParts = 0

    if (currWordCountFloor < int(phraseTup[4])):
        currWordCountFloor = int(phraseTup[4])
        lastWordCountFloorIdx = i-1

    initialIdx = lastWordCountFloorIdx

    # If the phrase has two or more words, it will try find smaller phrases or words that were already transformed in
    # PTB format and can be found in this phrase. First it will try find phrases that belong to the sentence. After
    # that, it will search ALL the phrases and words that were transformed in ptb format.
    if int(phraseTup[4]) > 1:

        # The first step is try find the smaller phrases in the sentence scope.
        tranfdDict = transformPhrase(phraseTup[0],
                                     [{'partPhrase':phraseTup[2].lower(),'isPtb':False}],
                                     phraseTup[4],
                                     sortedSentenceList,
                                     initialIdx,
                                     1,
                                     True
                                    )

        tranfdPhrase = []
        leftSearchbParts = 0

        if (tranfdDict != None):
          tranfdPhrase = tranfdDict['targetPhrase']
          leftSearchbParts = tranfdDict['leftParts']

        # If there is any part of the phrase that has not been found in the sentence scope, we will try find this left
        # parts in the global scope, in ALL the other phrases and words that were already transformed in PTB.
        if leftSearchbParts > 0:
            tranfdDict = transformPhraseFromMemory(phraseTup[0], tranfdPhrase, leftSearchbParts)

            if (tranfdDict != None):
                tranfdPhrase = tranfdDict['targetPhrase']
                leftSearchbParts = tranfdDict['leftParts']

        reconstructdTranfdPhrase = ""
        searchbPartsLeftStr = "|"


        # Rebuild the PTB phrase using all the fragments collected during the transformation phase.
        for tranfdPhrasePart in tranfdPhrase:
            if tranfdPhrasePart['isPtb']==False:
                if len(tranfdPhrase) > 1 and len(tranfdPhrasePart['partPhrase'].strip().split(" ")) == 1:
                    reconstructdTranfdPhrase = "%s (2 %s)" % (reconstructdTranfdPhrase,tranfdPhrasePart['partPhrase'])

                searchbPartsLeftStr = searchbPartsLeftStr + tranfdPhrasePart['partPhrase'] + "|"
            else:
                reconstructdTranfdPhrase = reconstructdTranfdPhrase + tranfdPhrasePart['partPhrase']

        ptbPhrase = "(%s %s)" % (str(phraseTup[3]),reconstructdTranfdPhrase)

        if leftSearchbParts > 0:
            global_totalPartsLeft[0] = global_totalPartsLeft[0] + leftSearchbParts
            sys.stderr.write("## LEFT phraseid:[%s] sentId:[%s] totalLeft:[%s] partsLeft:[%s] ############\n" % (
                                                str(phraseTup[0]),
                                                str(phraseTup[1]),
                                                str(leftSearchbParts),
                                                searchbPartsLeftStr)
            )



    # If the phrase has only one word it will format the ptb phrase with the word and its sentiment score. None
    # processing is done.
    else:
        ptbPhrase = "(%s %s)" % (str(phraseTup[3]),phraseTup[2])

    # Create a new tuple (0-phraseId | 1-sentenceId | 2-phrase | 3-sentiment | 4-wordsCount | 5-charsCount |6-ptbPhrase)
    # cloning the original one and replacing the ptbPhrase with the new one.
    newPhraseTupAux = (phraseTup[0],phraseTup[1],phraseTup[2],phraseTup[3],phraseTup[4],phraseTup[5],ptbPhrase)

    # Register the new tuple in the memory for future global queries
    if( (str(phraseTup[4]) in global_memPhrasesList) == False):
      global_memPhrasesList[str(newPhraseTupAux[4])] = {}

    global_memPhrasesList[str(newPhraseTupAux[4])][newPhraseTupAux[2].strip().lower()] = newPhraseTupAux

    # Replace the old tuple with this new one in the sentenceList. In this way, the other phrases of this sentence
    # will be able to use it in the future.
    sortedSentenceList[i] = newPhraseTupAux

    #Print the output
    if (str(phraseTup[0]) == phraseIdDebug or debug == False):
        # Feed the list with the new tuple: 0-phraseId | 1-sentenceId | 2-totalPartsLeft |
        #                                   3-PartsLeft | 4-phrase | 5-sentiment | 6-wordsCount |
        #                                   7-charsCount |8-ptbPhrase
        print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (str(phraseTup[0]),
                                                      str(phraseTup[1]),
                                                      str(leftSearchbParts),
                                                      searchbPartsLeftStr,
                                                      phraseTup[2],
                                                      str(phraseTup[3]),
                                                      str(phraseTup[4]),
                                                      str(phraseTup[5]),
                                                      ptbPhrase)

  return None


#######################################################################################################################
###################### M A I N   C O D E ##############################################################################
#######################################################################################################################
# This script gets the initial TSV file and transform the phrases to the PTB format. It will feed the file with some
# new columns of metadata that will be used in future process.


global_memPhrasesList = {}
global_memPhrasesList["0"]={}

global_currSentenceList = []
global_currSentenceId = -1
global_totalPartsLeft = [0]

print "phraseId\tsentenceId\ttotalPartsLeft\tPartsLeft\tphrase\tsentiment\twordsCount\tcharsCount\tptbPhrase"

# Doesnt use the first line: it is the header.
next(sys.stdin)

countLines = 0

for line in sys.stdin:
  countLines = countLines +1
  lineColumnsCount = 0
  try:
    # Format of input: phraseId\tsentenceId\tphrase\tsentiment
    # strip the line of leading and trailing whitespace,
    # then split into the four fields based on a tab delimiter
    lineColumns = line.strip().split("\t")
    lineColumnsCount = len(lineColumns)
    if (len(lineColumns)==2):
        lineColumns.append(".")

    if (len(lineColumns)==3):
        lineColumns.append("9")

    (phraseId, sentenceId, phrase, sentiment) = lineColumns
    wordsCount = len(phrase.strip().split(" "))
  except:
    sys.stderr.write("SKIPPED_LINES, %s [%s] \n"% (str(countLines),str(lineColumnsCount)) )
    continue
  
  # Process the previous sentence's group of phrase when the sentence ID found is different
  if (sentenceId != global_currSentenceId):
    procSentenceList(global_currSentenceList)
    global_currSentenceList = []

  # Format of each tuple: 0-phraseId | 1-sentenceId | 2-phrase | 3-sentiment | 4-wordsCount | 5-phraseLen | 6-ptbPhrase   
  global_currSentenceList.append( [phraseId, sentenceId, phrase, sentiment,wordsCount,len(phrase),""]  )
  global_currSentenceId = sentenceId

# Process the last sentence's group of phrase.
procSentenceList(global_currSentenceList)



sys.stderr.write("#####################################################################\n")
sys.stderr.write("##################### TOTAL LEFT [%s]      ##########################\n" %
                                str(global_totalPartsLeft[0]))

sys.stderr.write("#####################################################################\n")

