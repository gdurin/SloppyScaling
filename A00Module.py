from scipy import exp
import os
import SloppyScaling
reload(SloppyScaling)
import WindowScalingInfo as WS
reload(WS)
import Utils
reload(Utils)

name = 'A00' # This is the name used in the files

Xname = 's'
XscaledName = 'Ss'
Xscaled = "(s/W**(1.+zeta))"
#Xscaled = "(s*(1.0*k/L)**(sigma_k*(1.+zeta)))"
XscaledTeX = r'$s / W^{1+\zeta}$'

Yname = 'A00' # This must be the name of the module !!!!!!!!!
Ytheory = "(s*(k/L)**(sigma_k*(1.+zeta)))**(2.-tau) /s * exp(-(Ss*Ixs)**ns+U0)"
Yscaled = \
        "(1.0*k/L)**((sigma_k)*(tau-2.)*(1.+zeta)) * s**(tau-1.) * A00"
YscaledTeX = \
   r'${\cal{A}_{00}} = (k/L)^{\sigma_k (\tau-2) (1+\zeta)} s^{\tau-1} A_{00}$'

title = 'A(s,k,W): Area covered by avalanches of size S in window of width W'
scalingTitle = 'A(s,k,W) scaling function'

#
# Include corrections
#

# for large Ws, this should just be the A(s,k) below 
#Ytheory = "(1.0*k/L)**(sigma_k*(2.-tau)*(1.+zeta)) * S**(2.-tau) / S *exp(-((S**(1./(1.+zeta))*(1.0*k/L)**sigma_k)*Ixs)**ns+U0)"
#Ytheory_corrections= "exp(-U1/S)"
Ytheory_corrections = "(A0-A1/s+A2/s**2)"




# XXX Ixh_1 and Ixw_1 aren't used yet? More natural names?
parameterNames = "tau,sigma_k,zeta,ns,Ixs,U0"
#parameterNames_corrections = "U1"
parameterNames_corrections = "A0,A1, A2"
initialParameterValues = (1.18,0.39,0.79,1.6,7.07,-1.81)
#initialParameterValues_corrections = (0.1,)
initialParameterValues_corrections = (1.0,1.0,0.5)

if WS.corrections_to_scaling:
    Ytheory = Ytheory + "*" + Ytheory_corrections
    parameterNames = parameterNames + "," + parameterNames_corrections
    initialParameterValues = initialParameterValues + initialParameterValues_corrections


# If single independent parameter, must have comma after it -- makes it a tuple
theory = SloppyScaling.ScalingTheory(Ytheory, parameterNames, \
                initialParameterValues, WS.independentNames, \
                scalingX = Xscaled, scalingY = Yscaled, \
                scalingXTeX = XscaledTeX, \
                scalingYTeX = YscaledTeX, \
                title = title, \
                scalingTitle = scalingTitle, \
                Xname=Xname, XscaledName = XscaledName, \
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
