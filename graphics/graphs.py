from math import log2
from numpy import zeros, nan
from matplotlib.colors import Normalize
from matplotlib import cm

# derivative of the given polynomial
def differentiate(poly):
    n = len(poly) - 1
    return [(n - i) * an for (i, an) in enumerate(poly[:-1])]

def demJulia(p, dp, z, K, R, overflow):
    zk, dk = z, 1
    for _ in range(K):
        if max(
            abs(zk.real), abs(zk.imag),
            abs(dk.real), abs(dk.imag)
        ) > overflow: break
        dk = horner(dp, zk) * dk
        zk = horner(p, zk)
    abszk = abs(zk)
    if abszk < R: return 0
    else:
        absdk = abs(dk)
        if absdk == 0: return nan
        estimate = log2(abszk) * abszk / absdk
        return -log2(estimate)

def drawDemJulia(n, p, colormap, K, pow_, overflow):
    arr = zeros((n, n), dtype=float)
    dp = differentiate(p)
    r = radiusJulia(p)

    for i in range(n):
        for j in range(n):
            z = mapToComplexPlaneCenter(n, 0, r, i, j)
            arr[i,j] = demJulia(p, dp, z, K, r, overflow)

    m, M = arr.min(), arr.max()
    arr[arr == 0] = M
    arr[arr == nan] = M
    normalized = Normalize(m, M)(arr)
    adjusted = pow(normalized, pow_) # explained below
    colortable = colormap(adjusted)
            
    def rgbfun(i, j):
        if arr[i,j] == M: return (0,0,0)
        else: return colortable[i,j]

    drawImage('demJulia.png', rgbfun, n)
    
drawDemJulia(
    2000, [1, 0, -0.760+0.0698j], 
    cm.cubehelix.reversed(), 
    500, 0.8, 10**20
)