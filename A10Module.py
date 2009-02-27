import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,x
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

# what are corrections to theory? I'm leaving them similar to Ahk for now

name = 'A10' # This is the name used in the files
Ytheory = "((1.0*k/L)**(sigma_k))**((2.-tau)*(1.+zeta))*s**(1.-tau+1./(1.+zeta))/win*exp(-(Ss*(Iy0+Iy1*win*(1.0*k/L)**(sigma_k)))**n)"
Ytheory_corrections = "exp(Ah1/s+Ah2/s**2) \
                 *exp(Uh1*(s/win**(1.+zeta)) + Uh2/(s/win**(1.+zeta))"
Xname = 's'
Yname = 'A10' # This must be the name of the module !!!
# XXX Might want a YTeX name too?
scalingX = "(1.0*s/win**(1.+zeta))"
scalingXTeX = r'$ s / win^{1+\zeta} $'
scalingY = \
        "((1.0*k/L)**(sigma_k))**(-(2.-tau)*(1.+zeta)) * s**(-1.+tau-1./(1.+zeta)) * win * A10"
scalingYTeX = \
   r'${\cal{A}_{10}} = ((k/L)^{\sigma_k})^{-(2.-\tau) (1.+\zeta)} s^{-1.+\tau-1./(1.+\zeta)} win A_{10}$'
title = 'A(s,k,win): Area covered by avalanches of size s in window of width win'
scalingTitle = 'A(s,k,win) scaling function'
# XXX Ixh_1 and Ixw_1 aren't used yet? More natural names?
parameterNames = "tau,sigma_k,zeta,Iy0,Iy1,n"
parameterNames_corrections = "A1,A2,U1,U2"
initialParameterValues = (1.22,0.43,0.75,1.0,1.0,2.0)
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

for independent in WS.independentValues:
    k, L, win = independent
    fileName = WS.dataDirectory + name + "_W=" + str(win).rjust(4, str(0))+"_k"+ str(k) + "_System_Size=" + str(2*L) + "x" + str(L) + "_"+ WS.simulType + ".bnd"
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[independent], \
        pointColor=WS.Color[independent], \
        initialSkip = WS.rows_to_skip)

f = __file__
f = f.split("/")[-1]
thisModule = f.split('Module.py')[0]
exec(thisModule + "= SloppyScaling.Model(theory, data, name)")
