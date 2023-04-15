__author__ = 'Jered Stratton'
# Set Mobile threshold using method of Shoji et al.
import sys
import math
import statistics
import numpy
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

base = importr('base')
utils = importr('utils')
inflection = importr('inflection')
MASS = importr('MASS')
dplyr = importr('dplyr')
stats = importr('stats')

def mobilityThreshold(trajFileName):
    """Build dataframe of distances from trajectory file, and use it to compute and return a mobility threshold"""
    frameCount = 1
    distances = []
    trajFile = open(trajFileName, 'r')
    trajFile.readline()
    trajFile.readline()
    line = trajFile.readline()
    line = line.rstrip()
    lineValues = line.split('\t')
    xPrev = float(lineValues[1])
    yPrev = float(lineValues[2])
    for line in trajFile:
        line = line.rstrip()
        lineValues = line.split('\t')
        xCur = float(lineValues[1])
        yCur = float(lineValues[2])
        distanceCur = math.sqrt((xCur - xPrev) ** 2 + (yCur - yPrev) ** 2)
        if distanceCur >= 25:
            print("Warning: >25 pixels traveled at frame " + str(frameCount))
        else:
            distances.append(distanceCur)
        frameCount += 1
        xPrev = xCur
        yPrev = yCur

    trajFile.close()
    distances = robjects.FloatVector(distances)
    density = stats.density(distances)
    densityX = list(density.rx2(1))
    densityY = list(density.rx2(2))
    sliceIndex = densityY.index(max(densityY))
    densityX = densityX[sliceIndex:]
    densityY = densityY[sliceIndex:]
    sliceIndex = numpy.searchsorted(densityX, 5)
    densityX = densityX[:sliceIndex]
    densityY = densityY[:sliceIndex]
    densityX = robjects.FloatVector(densityX)
    densityY = robjects.FloatVector(densityY)
    kneepoint = inflection.uik(densityX, densityY)
    mobileThresh = float(kneepoint[0])

    print("Mobile threshold set at " + str(mobileThresh) + " pixels")
    return (mobileThresh, frameCount)