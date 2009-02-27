import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

name = 'A00' # This is the name used in the files
Ytheory = "(s*(1.0*k/L)**(sigma_k*(1.+zeta)))**(2.-tau)* (1./s) * exp(-(Ss*Ixs)**ns+U0)"
# for large Ws, this should just be the A(s,k) below 
#Ytheory = "(1.0*k/L)**(sigma_k*(2.-tau)*(1.+zeta)) * (1.0*s)*(2.-tau) *(1./s)*exp(-((s**(1./(1.+zeta))*(1.0*k/L)**sigma_k)*Ixs)**ns+U0)"
#Ytheory_corrections= "exp(-U1/s)"
Ytheory_corrections = "(A0-A1/s+A2/s**2)"
Xname = 's'
Yname = 'A00' # This must be the name of the module !!!!!!!!!
# XXX Might want a YTeX name too?
scalingX = "(1.0*s/win**(1.+zeta))"
#scalingX = "(s*(1.0*k/L)**(sigma_k*(1.+zeta)))"
scalingXTeX = r'$s / win^{1.+\zeta}$'
scalingY = \
        "(1.0*k/L)**((sigma_k)*(tau-2.)*(1.+zeta)) * (1.0*s)**(tau-1.) * A00"
scalingYTeX = \
   r'${\cal{A}_{00}} = (k/L)^{\sigma_k (\tau-2.) (1.+\zeta)} s^{\tau-1.} A_{00}$'

title = 'A(s,k,win): Area covered by avalanches of size s in window of width win'
scalingTitle = 'A(s,k,win) scaling function'
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
                scalingX = scalingX, scalingY = scalingY, \
                scalingXTeX = scalingXTeX, \
                scalingYTeX = scalingYTeX, \
                title = title, \
                scalingTitle = scalingTitle, \
                Xname=Xname, Yname=Yname, normalization = WS.normalization)

data = SloppyScaling.Data()
for independent in WS.independentValues:
    k, L, win = independent
    fileName = WS.dataDirectory  +  name + "_W="+str(win).rjust(4, str(0))+"_k" + str(k) \
        + "_System_Size=" + str(2*L) + "x" + str(L) + "_"+ WS.simulType + ".bnd" 
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[independent], \
        pointColor=WS.Color[independent], \
        initialSkip = WS.rows_to_skip)


f = __file__
f = f.split("/")[-1]
thisModule = f.split('Module.py')[0]
exec(thisModule + "= SloppyScaling.Model(theory, data, name)")
