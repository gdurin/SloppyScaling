import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

# what are corrections to theory? I'm leaving them similar to Ahk for now

name = 'A00' # This is the name used in the files
Ytheory = "(k**(sigma_k))**((2.-tau)*(1.+zeta))*s**(1.-tau) \
            *exp(-(s/w**((1.+zeta))*Ixh_0)**nh)"
Ytheory_corrections = "exp(Ah1/s+Ah2/s**2) \
                 *exp(Uh1*(s/w**(1.+zeta)) + Uh2/(s/w**(1.+zeta)))"
Xname = 's'
Yname = 'A00' # This must be the name of the module !!!!!!!!!
# XXX Might want a YTeX name too?
scalingX = "s/w**(1.+zeta)"
scalingXTeX = r'$s / w^{1.+\zeta}$'
scalingY = \
        "(k**(-sigma_k))**(-(2.-tau)*(1.+zeta)) * s**(tau-1.) * A00"
scalingYTeX = \
   r'$(k^{\sigma_k})^{-(2.-\tau) (1.+\zeta)} s^{tau-1.} {\cal{A}}_{00}$'
title = 'A(s,k,w): Area covered by avalanches of size s in window of width w'
scalingTitle = 'A(s,k, w) scaling function'
# XXX Ixh_1 and Ixw_1 aren't used yet? More natural names?
parameterNames = "tau,sigma_k,zeta,Ixh_0,nh"
parameterNames_corrections = "Ah1,Ah2,Uh1,Uh2"
initialParameterValues = (1.2,0.4,0.6,2e-2,1.4)
initialParameterValues_corrections = (0.,0.,0.,0.)

if WS.corrections_to_scaling:
    Ytheory = Ytheory + "*" + Ytheory_corrections
    parameterNames = parameterNames + "," + parameterNames_corrections
    initialParameterValues = initialParameterValues + initialParameterValues_corrections


# If single independent parameter, must have comma after it -- makes it a tuple
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
        + "_" + WS.systemSize + "_"+ WS.simulType + ".bnd"
    independent = (k,) # Must be a tuple
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[k], \
        pointColor=WS.Color[k], \
        initialSkip = WS.rows_to_skip)

f = __file__
f = f.split("/")[-1]
thisModule = f.split('Module.py')[0]
exec(thisModule + "= SloppyScaling.Model(theory, data, name)")
