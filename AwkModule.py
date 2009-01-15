import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

name = 'A_w_k' # This is the name used in the files
Ytheory = "(w*k**sigma_k)**((2.-tau)*(1.+zeta))\
                 *(1./w)*exp(-((w*k**sigma_k)*Ixw_0)**nw)"
Ytheory_corrections = "exp(Aw1/w+Aw2/w**2) * exp(Uw1*(w*k**sigma_k)+Uw2/(w*k**sigma_k))"
                 
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
parameterNames = "tau,sigma_k,zeta,Ixw_0,nw"
parameterNames_corrections = "Aw1,Aw2,Uw1,Uw2"
initialParameterValues = (1.2,0.4,0.6,2e-2,1e-1)
initialParameterValues_corrections = (0.,0.,0.,0.)


if WS.corrections_to_scaling:
    Ytheory = Ytheory + "*" + Ytheory_corrections
    parameterNames = parameterNames + "," + parameterNames_corrections
    initialParameterValues = initialParameterValues + initialParameterValues_corrections


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
    fileName = WS.dataDirectory + name + str(k) \
        + "_" + WS.systemSize + "_"+ WS.simulType + ".bin"
    independent = (k,) # Must be a tuple
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[k], \
        pointColor=WS.Color[k], \
        initialSkip = WS.rows_to_skip)
Awk = SloppyScaling.Model(theory, data, name)
