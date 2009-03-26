from scipy import exp
import os
import WindowScalingInfo as WS
reload(WS)
import SloppyScaling
reload(SloppyScaling)
import Utils
reload(Utils)


name = 'A_h' # This is the name used in the files

Xname = 'h'
XscaledName = 'hs'
Xscaled = "h*k**(zeta*sigma_k)"
XscaledTeX = r'$h k^{\zeta \sigma_k}$'

Yname = 'Ahk' # This must be the name of the module !!!!!!!!!
Ytheory = "hs**((2.-tau)*(1.+zeta)/zeta) \
            /h *exp(-(hs*Ixh_0)**nh)"
Yscaled = "hs**(-(2.-tau)*(1.+zeta)/zeta) * h * Ahk"
YscaledTeX = \
   r'$(h k^{\zeta \sigma_k})^{-(2-\tau) (1+\zeta)/\zeta} h {\cal{A}}_{hk}$'

title = 'A(h,k): Area covered by avalanches of height h'
scalingTitle = 'A(h,k) scaling function'


#
# Include corrections
#
Ytheory_corrections = "exp(Ah1/h+Ah2/h**2) \
                 *exp(Uh1*(h*k**(zeta*sigma_k)) + Uh2/(h*k**(zeta*sigma_k)))"

parameterNames = "tau,sigma_k,zeta,Ixh_0,nh"
parameterNames_corrections = "Ah1,Ah2,Uh1,Uh2"
initialParameterValues = (1.2,0.4,0.6,2e-2,1.4)
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
