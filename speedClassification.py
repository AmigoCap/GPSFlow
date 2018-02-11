from scipy.cluster.vq import vq,kmeans,whiten
import numpy as np

def applyKMeans(seg,k):
    lV=[]
    for ii, v in enumerate(seg['velocity']):
        lV.append([float(ii),v])

    features  = np.array(lV)
    whitened = whiten(features)
    k=kmeans(whitened,k)

    lK=[]
    for ii in range(len(k[0])):
        lK.append(k[0][ii][0])
    return (sorted(lK),whitened)


def getBoundiaries(lK):
    lBoundiaries=[0]
    for ii in range (len(lK)-1):
        lBoundiaries.append((lK[ii]+lK[ii+1])/2)
    lBoundiaries.append(100)
    return lBoundiaries

def calcFirstSegmentation(lBoundiaries,whitened):
    lFirstSpeedSegmentation=[[] for ii in range (len(lBoundiaries)-1)]
    for ii in range(len(whitened)):
        for jj in range(len(lBoundiaries)-1):
            if whitened[ii][0]>lBoundiaries[jj] and whitened[ii][0]<lBoundiaries[jj+1]:
                lFirstSpeedSegmentation[jj].append(whitened[ii][1])
                for kk in range(jj+1,len(lFirstSpeedSegmentation)):
                    lFirstSpeedSegmentation[kk].append(-1.0)
    return lFirstSpeedSegmentation

def calcSpeedTreend(i):
    if i < 0.4:
        return 0
    elif i>2.0:
        return 2
    else:
        return 1

def setToZero(i):
    if i<=0:
        return 0
    else:
        return i

def concacatenateLists(speedTrend,lS):
    lSf=[lS[0]]
    a=[speedTrend[0]]
    for ii in range(0,len(speedTrend)-1):
        if speedTrend[ii]==speedTrend[ii+1]:
            lSf[-1]=lSf[-1]+list(filter(lambda x : x>=0 ,lS[ii+1]))
        else:
            lSf.append(list(map(setToZero,lS[ii+1])))
            a.append(speedTrend[ii+1])
    return lSf,a


def calcMean(lFirstSpeedSegmentation):
    return([np.mean(list(filter(lambda x: x > 0, segment))) for segment in lFirstSpeedSegmentation])

def agglomerateSpeedSegments(lFirstSpeedSegmentation):
    lMeans=calcMean(lFirstSpeedSegmentation)
    speedTrend=[calcSpeedTreend(meanSpeed) for meanSpeed in lMeans ]
    (l,a)=(concacatenateLists(speedTrend,lFirstSpeedSegmentation))
    return (l,a)