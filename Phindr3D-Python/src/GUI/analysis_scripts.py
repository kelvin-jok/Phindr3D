import numpy as np

def getImageThreshold(IM):
    """called in getIndividualChannelThreshold"""
    maxBins = 256
    freq, binEdges = np.histogram(IM.flatten(), bins=maxBins)
    binCenters = binEdges[:-1] + np.diff(binEdges) / 2
    meanIntensity = np.mean(IM.flatten())
    numThresholdParam = len(freq)
    binCenters -= meanIntensity
    den1 = np.sqrt((binCenters ** 2) @ freq.T)
    numAllPixels = np.sum(
        freq)  # freq should hopefully be a 1D vector so summ of all elements should be right.
    covarMat = np.zeros(numThresholdParam)
    for iThreshold in range(numThresholdParam):
        numThreshPixels = np.sum(freq[binCenters > binCenters[iThreshold]])
        den2 = np.sqrt((((numAllPixels - numThreshPixels) * (numThreshPixels)) / numAllPixels))
        if den2 == 0:
            covarMat[iThreshold] = 0  # dont want to select these, also want to avoid nans
        else:
            covarMat[iThreshold] = (binCenters @ (freq * (binCenters > binCenters[iThreshold])).T) / (
                        den1 * den2)  # i hope this is the right mix of matrix multiplication and element-wise stuff.
    imThreshold = np.argmax(covarMat)  # index makes sense here.
    imThreshold = binCenters[imThreshold] + meanIntensity
    return imThreshold

def getImageWithSVMVOverlay(IM, param, type):
    """
    I assume this means get image with superVoxel or megaVoxel overlay.
    % param.tileX = 10;
    % param.tileY = 10;
    % param.megaVoxelTileX = 5;
    % param.megaVoxelTileY = 5;
    """

    if type == 'SV':
        IM[range(0,IM.shape[0],param.tileX), :,:] = 0.7
        IM[:, range(0,IM.shape[1],param.tileY),:] = 0.7
    else:
        IM[range(0,IM.shape[0],param.tileX*param.megaVoxelTileX), :,:] = 1
        IM[:, range(0,IM.shape[1], param.tileY*param.megaVoxelTileY),:] = 1
    return IM