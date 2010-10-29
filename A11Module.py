from scipy import exp
import os
import SloppyScaling
reload(SloppyScaling)
import WindowScalingInfo as WS
reload(WS)
import Utils
reload(Utils)


name = 'A11' # This is the name used in the files

Xname = 's'
XscaledName = 'Ss'
Xscaled = '(s*(1.0*k/L)**(sigma_k*zeta)/W)'
XscaledTeX = r'$s (k/L)^{\sigma_k \zeta}/W$'
WscaledName = "Ws"
Wscaled = '(W*(1.0*k/L)**(sigma_k))'


Yname = 'A11' # This must be the name of the module !!!
Ytheory = 'Ss**((2.-tau)*(1.+zeta)/zeta)/s*exp(-1.0*Ss**nh*Ixh)'
#Ytheory = Ss+'**((2.-tau)*(1.+zeta)/zeta)/s*exp(-1.0*('+Ss+'-c)**nh*Ixh)'
Yscaled = 'Ss**((tau-2.)*(1.+zeta)/zeta)*s*A11'       
YscaledTeX = \
   r'$(s (k/L)^{\sigma_k \zeta}/W)^{(\tau-2) (1+\zeta)/\zeta} s {\cal{A}_{11}}$'

title = 'A11(s,k,W): Area covered by avalanches of size S in window of width W'
scalingTitle = 'A11(s,k,W) scaling function'


#
# Include corrections
#

Ytheory_corrections = "exp(U0-U1*Ws**n2/Ss**n3)"
#Ytheory_corrections = "exp(U0-U1*"+Ws+"**n2/Ss**n3-Ux*"+Ws+"**n4/Ss**n5)"
#Ytheory_corrections = "exp(U0-U1*"+Ws+"/(1.0*Ss)+U2*"+Ws+"/(1.0*Ss**2.))"
#Ytheory_corrections = "exp(Ah1/s+Ah2/s**2)*exp(Uh1*(s*(1.0*k/L)**sigma_k/win**(1.+zeta)) + Uh2/(s*(k/L)**sigma_k/win**(1.+zeta)))"
#



parameterNames = "tau,sigma_k,zeta,Ixh,nh"
parameterNames_corrections = "U0,U1,n2,n3"
#parameterNames_corrections = "U0,U1,n2,n3,Ux,n4,n5"
#parameterNames_corrections = "U0,  U1, U2"
#initialParameterValues = (2.0, 0.4, 1.0, 1.8 ,2.0, 1.0)
initialParameterValues = (1.2, 0.38, 0.85, 3.0, 2.0)
#initialParameterValues_corrections = (0.0,0.0,1000.0,0.0)
initialParameterValues_corrections = (1.0, 0.5, 1.0, 1.0)
#initialParameterValues_corrections =(1.0, 0.6,0.7,1.5, 0.5,0.7, 1.5)
#initialParameterValues_corrections = (2.0, 0.5, 0.0)

# Correct if spaces are included in the parameters names
parameterNames = parameterNames.replace(" ","")
parameterNames_corrections = parameterNames_corrections.replace(" ","")

if WS.corrections_to_scaling:
    Ytheory = Ytheory + "*" + Ytheory_corrections
    parameterNames = parameterNames + "," + parameterNames_corrections
    initialParameterValues = initialParameterValues + initialParameterValues_corrections
 

theory = SloppyScaling.ScalingTheory(Ytheory, parameterNames, \
                initialParameterValues, WS.independentNames, \
                scalingX = Xscaled, scalingY = Yscaled, scalingW = Wscaled,\
                scalingXTeX = XscaledTeX, \
                scalingYTeX = YscaledTeX, \
                title = title, \
                scalingTitle = scalingTitle, \
                Xname=Xname, XscaledName=XscaledName, \
                Yname=Yname, WscaledName = WscaledName, \
                normalization = WS.normalization)

data = SloppyScaling.Data()

loaded = 0
for independent in WS.independentValues:
    L, k, W = independent
    ext =  "_" + WS.simulType + ".bnd"
    if os.getlogin() == 'yj':
        k_string = "_k"
    else:
        k_string = "_k="
    fileName = "".join([WS.dataDirectory,name,"_W=",str(W).rjust(4, str(0)),\
                        k_string,str(k), "_L=",str(2*L), "x", str(L), ext])
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
