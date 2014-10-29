#!/usr/bin/env python

import sys

for line in sys.stdin:
    try:
        line.replace("\s","\t")
        (lineNumber,labelIdx,rootIdx) = line.strip().split("\t")
    except:
        continue

    labelIdx = labelIdx.replace(",",".")
    fltLabelIdx = float(labelIdx)
    incorrectLabels = 82588 - (82588*fltLabelIdx)

    newFltLabelIdx = (26102-incorrectLabels)/26102


    print "%s\t%.4f\t%s" % (str(lineNumber),newFltLabelIdx,str(rootIdx))