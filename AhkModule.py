import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

name = 'Ahk'
Ytheory = "(h*k**(zeta*sigma_k))**((2.-tau)*(1.+zeta)/zeta)\
                 *exp(Ah1/h+Ah2/h**2) \
                 *exp(Uh1*(h*k**(zeta*sigma_k)) \
                    +Uh2/(h*k**(zeta*sigma_k))) \
                 *(1./h)*exp(-((h*k**(zeta*sigma_k))*Ixh_0)**nh)"

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
parameterNames = "tau,sigma_k,zeta,Ixh_0,Ixh_1,nh,Ah1,Ah2,Uh1,Uh2"
initialParameterValues = (1.,0.4,0.6,2e-2,1e-1,1.4,0.,0.,0.,0.)

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
    fileName = WS.dataDirectory + "A_h_k" + str(k) \
        + "_System_Size=2048x1024_NonLinear.bin"
    independent = (k,) # Must be a tuple
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[k], \
        pointColor=WS.Color[k]) 
Ahk = SloppyScaling.Model(theory, data, name)
