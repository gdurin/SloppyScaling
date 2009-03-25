from scipy import exp
import os
import SloppyScaling
reload(SloppyScaling)
import WindowScalingInfo as WS
reload(WS)
import Utils
reload(Utils)


name = 'A10' # This is the name used in the files

Xname = 's'
XscaledName = 'Ss'
Xscaled = "(s/W**(1.+zeta))"
XscaledTeX = r'$s / W^{1+\zeta}$'

Yname = 'A10' # This must be the name of the module !!!
Ytheory = "((1.0*k/L)**(sigma_k))**((2.-tau)*(1.+zeta))*s**(1.-tau+1./(1.+zeta))/W*exp(-(Ss*(Iy0+Iy1*W*(1.0*k/L)**(sigma_k)))**n)"
Yscaled = \
        "((1.0*k/L)**(sigma_k))**(-(2.-tau)*(1.+zeta)) * s**(-1.+tau-1./(1.+zeta)) * W * A10"
scalingYTeX = \
   r'${\cal{A}_{10}} = ((k/L)^{\sigma_k})^{-(2-\tau) (1+\zeta)} s^{-1+\tau-1/(1+\zeta)} W A_{10}$'

title = 'A(s,k,W): Area covered by avalanches of size s in window of width win'
scalingTitle = 'A(s,k,win) scaling function'

#
# Include corrections
#
Ytheory_corrections = "exp(Ah1/s+Ah2/s**2)*exp(Uh1*Ss + Uh2/Ss)"

parameterNames = "tau,sigma_k,zeta,Iy0,Iy1,n"
parameterNames_corrections = "A1,A2,U1,U2"
initialParameterValues = (1.22,0.43,0.75,1.0,1.0,2.0)
initialParameterValues_corrections = (0.,0.,0.,0.)


# Correct if spaces are included in the parameters names
parameterNames = parameterNames.replace(" ","")
parameterNames_corrections = parameterNames_corrections.replace(" ","")

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
                Xname=Xname, XscaledName=XscaledName, \
                Yname=Yname, \
                fixParameter = WS.fixParameter,\
                fixedParameters = WS.fixedParameters, \
                normalization = WS.normalization)

data = SloppyScaling.Data()

for independent in WS.independentValues:
    L, k, W = independent
    ext =  "_" + WS.simulType + ".bnd"
    if os.getlogin() == 'yj':
        k_string = "_k"
    else:
        k_string = "_k="
    fileName = "".join([WS.dataDirectory,name,"_W=",str(W).rjust(4, str(0)),\
                        k_string,str(k), "_System_Size=",str(2*L), "x", str(L), ext])
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[independent], \
        pointColor=WS.Color[independent], \
        initialSkip = WS.rows_to_skip)


f = __file__
f = f.split("/")[-1]
thisModule = f.split('Module.py')[0]
exec(thisModule + "= SloppyScaling.Model(theory, data, name, WS.sortedValues)")
