from scipy import exp
import os
import SloppyScaling
reload(SloppyScaling)
import WindowScalingInfo as WS
reload(WS)
import Utils
reload(Utils)


name = 'A_w' # This is the name used in the files

Xname = 'w'
XscaledName = 'ws'
Xscaled = "w*k**(sigma_k)"
XscaledTeX = r"$w k^{\sigma_k}$"

Yname = 'Awk' # This must be the name of the module !!!!!!!!!
Ytheory = "ws**((2.-tau)*(1.+zeta))/w*exp(-(ws*Ixw_0)**nw)"
Yscaled = "ws**(-(2.-tau)*(1.+zeta)) * w * Awk"
YscaledTeX = r'$(w k^{\sigma_k})^{-(2-\tau) (1+\zeta)} w A_{wk}$'

title = 'A(w,k): Area covered by avalanches of width w'
scalingTitle = 'A(w,k) scaling function'


#
# Include corrections
#
Ytheory_corrections = "exp(Aw1/w+Aw2/w**2) * exp(Uw1*ws+Uw2/ws)"


parameterNames = "tau,sigma_k,zeta,Ixw_0,nw"
parameterNames_corrections = "Aw1,Aw2,Uw1,Uw2"
initialParameterValues = (1.2,0.4,0.6,2e-2,1e-1)
initialParameterValues_corrections = (0.,0.,0.,0.)

# Correct if spaces are included in the parameters names
parameterNames = parameterNames.replace(" ","")
parameterNames_corrections = parameterNames_corrections.replace(" ","")

if WS.corrections_to_scaling:
    Ytheory = Ytheory + "*" + Ytheory_corrections
    parameterNames = parameterNames + "," + parameterNames_corrections
    initialParameterValues = initialParameterValues + initialParameterValues_corrections


theory = SloppyScaling.ScalingTheory(Ytheory, parameterNames, \
                initialParameterValues, WS.independentNames, \
                scalingX = Xscaled, scalingY = Yscaled, \
                scalingXTeX = XscaledTeX, \
                scalingYTeX = YscaledTeX, \
                title = title, \
                scalingTitle = scalingTitle, \
                Xname=Xname, XscaledName=XscaledName, \
                Yname=Yname, \
                normalization = WS.normalization)

data = SloppyScaling.Data()

loaded = 0
for independent in WS.independentValues:
    L, k = independent
    ext =  "_" + WS.simulType + ".bnd"
    if os.getlogin() == 'yj':
        k_string = "_k"
    else:
        k_string = "_k="
    fileName = "".join([WS.dataDirectory,name,\
                        k_string,str(k), "_System_Size=",str(2*L), "x", str(L), ext])
    success = data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[independent], \
        pointColor=WS.Color[independent], \
        initialSkip = WS.rows_to_skip)
    loaded += success

nFiles = len(WS.independentValues)
if loaded ==  nFiles:
    print "Loaded %2d/%2d files (%s)" % (loaded, nFiles, name)
else:
    print "====================="
    print "Attention! %2d/%2d files are missing (%s)" %  (nFiles-loaded, nFiles, name)
    print "====================="

f = __file__
f = f.split("/")[-1]
thisModule = f.split('Module.py')[0]
exec(thisModule + "= SloppyScaling.Model(theory, data, name, WS.sortedValues)")
