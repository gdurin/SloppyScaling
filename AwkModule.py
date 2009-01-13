import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

name = 'Awk'
Ytheory = "(w*k**sigma_k)**((2.-tau)*(1.+zeta))\
                 *exp(Aw1/w+Aw2/w**2) \
                 *exp(Uw1*(w*k**sigma_k) \
                    +Uw2/(w*k**sigma_k)) \
                 *(1./w)*exp(-((w*k**sigma_k)*Ixw_0)**nw)"

Xname = 'w'
# XXX Might want a YTeX name too?
Yname = 'Awk'
scalingX = "w*k**(sigma_k)"
scalingXTeX = "$w k^{\sigma_k}$"
scalingY = \
        "(w*k**sigma_k)**(-(2.-tau)*(1.+zeta)) * w * Awk"
scalingYTeX = \
   '$(w k^{\sigma_k})^{-(2.-\\tau) (1.+\zeta)} w A_{wk}$'
title = 'A(w,k): Area covered by avalanches of width w'
scalingTitle = 'A(w,k) scaling function'
# XXX Ixh_1 and Ixw_1 aren't used yet? More natural names?
parameterNames = "tau,sigma_k,zeta,Ixw_0,Ixw_1,nw,Aw1,Aw2,Uw1,Uw2"
initialParameterValues = (1.,0.4,0.6,2e-2,1e-1,2.,0.,0.,0.,0.)

theory = SloppyScaling.ScalingTheory(Ytheory, parameterNames, \
                initialParameterValues, WS.independentNames, \
                scalingX = scalingX, scalingY = scalingY, \
                scalingXTeX = scalingXTeX, \
                scalingYTeX = scalingYTeX, \
                title = title, \
                scalingTitle = scalingTitle, \
                Xname=Xname, Yname=Yname, normalization = WS.normalization)

data = SloppyScaling.Data()
for k in WS.independentValues:
    fileName = WS.dataDirectory + "A_w_k" + str(k) \
        + "_System_Size=2048x1024_NonLinear.bin"
    independent = (k,) # Must be a tuple
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[k], pointColor=WS.Color[k]) 
Awk = SloppyScaling.Model(theory, data, name)
