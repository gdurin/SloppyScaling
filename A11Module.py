import SloppyScaling
reload(SloppyScaling)
from scipy import exp

# Includes dataDirectory, independentNames, independentValues,
# and Symbol, Color dictionaries
import WindowScalingInfo as WS
reload(WS)

#need to change Ss back to be in the equation...
#but I'll leave this this way now...

name = 'A11' # This is the name used in the files
#Ytheory = "(k/L)**((-sigma_k)*(tau-2.)*(1.+zeta))"
#Ss = '(s*(1.0*k/L)**(sigma_k*zeta)/win)'
#get rid of this with new software, and we can make Ss a variable now...
Ytheory = 'Ss**((2.-tau)*(1.+zeta)/zeta)*(1./s)*exp(-1.0*Ss**nh*Ixh)'
#Ytheory = Ss+'**((2.-tau)*(1.+zeta)/zeta)*(1./s)*exp(-1.0*('+Ss+'-c)**nh*Ixh)'
Ws = '(win*(1.0*k/L)**(sigma_k))'
Ytheory_corrections = "exp(U0-U1*"+Ws+"**n2/Ss**n3)"
#Ytheory_corrections = "exp(U0-U1*"+Ws+"**n2/Ss**n3-Ux*"+Ws+"**n4/Ss**n5)"
#Ytheory_corrections = "exp(U0-U1*"+Ws+"/(1.0*Ss)+U2*"+Ws+"/(1.0*Ss**2.))"
#Ytheory_corrections = "exp(Ah1/s+Ah2/s**2)*exp(Uh1*(s*(1.0*k/L)**sigma_k/win**(1.+zeta)) + Uh2/(s*(k/L)**sigma_k/win**(1.+zeta)))"
Xname = 's'
Yname = 'A11' # This must be the name of the module !!!
# XXX Might want a YTeX name too?
scalingX = '(s*(1.0*k/L)**(sigma_k*zeta)/win)'
scalingXTeX = r'$s (k/L)^{\sigma_k \zeta}/win$'
scalingY = 'Ss**((tau-2.)*(1.+zeta)/zeta)*s*A11'       
scalingYTeX = \
   r'$(s (k/L)^{\sigma_k \zeta}/win)^{(\tau-2.) (1.+\zeta)/\zeta} s {\cal{A}_{11}}$'
title = 'A11(s,k,win): Area covered by avalanches of size s in window of width win'
scalingTitle = 'A11(s,k,win) scaling function'
# XXX Ixh_1 and Ixw_1 aren't used yet? More natural names?
parameterNames = "tau,sigma_k,zeta,Ixh, nh"
#parameterNames_corrections = "Ah1,Ah2,Uh1,Uh2,"
parameterNames_corrections = "U0,U1,n2,n3"
#parameterNames_corrections = "U0,U1,n2,n3,Ux,n4,n5"
#parameterNames_corrections = "U0,  U1, U2"
#initialParameterValues = (2.0, 0.4, 1.0, 1.8 ,2.0, 1.0)
initialParameterValues = (1.2, 0.38, 0.85, 3.0, 2.0)
#initialParameterValues_corrections = (0.0,0.0,1000.0,0.0)
initialParameterValues_corrections = (1.0, 0.5, 1.0, 1.0)
#initialParameterValues_corrections =(1.0, 0.6,0.7,1.5, 0.5,0.7, 1.5)
#initialParameterValues_corrections = (2.0, 0.5, 0.0)

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
    fileName = WS.dataDirectory + name +"_W="+str(win).rjust(4, str(0))+"_k"+ str(k) + "_System_Size=" + str(2*L) + "x" + str(L) + "_"+ WS.simulType + ".bnd"
    data.InstallCurve(independent, fileName, \
        pointSymbol=WS.Symbol[independent], \
        pointColor=WS.Color[independent], \
        initialSkip = WS.rows_to_skip)

f = __file__
f = f.split("/")[-1]
thisModule = f.split('Module.py')[0]
exec(thisModule + "= SloppyScaling.Model(theory, data, name)")
