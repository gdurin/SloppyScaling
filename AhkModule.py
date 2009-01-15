import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

name = 'A_h_k' # This is the name used in the files
Ytheory = "(h*k**(zeta*sigma_k))**((2.-tau)*(1.+zeta)/zeta) \
            *(1./h)*exp(-((h*k**(zeta*sigma_k))*Ixh_0)**nh)"
Ytheory_corrections = "exp(Ah1/h+Ah2/h**2) \
                 *exp(Uh1*(h*k**(zeta*sigma_k)) + Uh2/(h*k**(zeta*sigma_k)))"
Xname = 'h'
Yname = 'Ahk'
# XXX Might want a YTeX name too?
scalingX = "h*k**(zeta*sigma_k)"
scalingXTeX = r'$h k^{\zeta \sigma_k}$'
scalingY = \
        "(h*k**(zeta*sigma_k))**(-(2.-tau)*(1.+zeta)/zeta) * h * Ahk"
scalingYTeX = \
   r'$(h k^{\zeta \sigma_k})^{-(2.-\tau) (1.+\zeta)/\zeta} h {\cal{A}}_{hk}$'
title = 'A(h,k): Area covered by avalanches of height h'
scalingTitle = 'A(h,k) scaling function'
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
        + "_" + WS.systemSize + "_"+ WS.simulType + ".bin"
    independent = (k,) # Must be a tuple
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[k], \
        pointColor=WS.Color[k], \
        initialSkip = WS.rows_to_skip)
    
Ahk = SloppyScaling.Model(theory, data, name)
