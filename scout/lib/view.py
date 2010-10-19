import sys


def printPercentUpdate(currentCount, totalCount):
    printDirectly('\r% 3d %% \t%d        ' % (100 * currentCount / totalCount, currentCount))


def printPercentFinal(totalCount):
    printDirectly('\r100 %% \t%d        \n' % totalCount)


def printDirectly(feedback):
    sys.stdout.write(feedback)
    sys.stdout.flush()
