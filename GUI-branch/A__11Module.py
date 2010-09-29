from scipy import exp
import os, sys, pickle
import scalingtheory
reload(scalingtheory)
import WindowScalingInfo as WS
reload(WS)
import Utils
reload(Utils)
import SloppyScaling
reload(SloppyScaling)
import string2latex


dirImages, dirFiles = 'images','files'
f = __file__
f = f.split("/")[-1]
thisModule = f.split('Module.py')[0]
filePkl = ".".join([thisModule,"pkl"])
filePkl = os.path.join(dirFiles,filePkl)
F = open(filePkl, 'rb')
fvars = pickle.load(F)


#try:
    #F = open(filePkl, 'rb')
    #fvars = pickle.load(F)
#except:
    #print "There is an error in the file : "+ filePkl
    #sys.exit()

name = fvars['Yname'] # This is the name used in the files
name = name.replace("__","")

fvars['initialParameterValues'] = (1.4, 0.38, 0.85, 2.0, 2.0)

fvars['deriv'] = fvars['derivNoCorrections']

if WS.corrections_to_scaling:
    fvars['Yvalue'] = fvars['Yvalue'] + fvars['Ysign'] + fvars['Ycorrections']
    fvars['initialParameterValues_corrections'] = (1.0, 0.5, 1.0, 1.0)
    fvars['parameterNames'] = fvars['parameterNames'] + "," + fvars['parameterNames_corrections']
    fvars['initialParameterValues'] = fvars['initialParameterValues'] + fvars['initialParameterValues_corrections']
    fvars['deriv'] = fvars['derivWithCorrections']
    
#print fvars['independent']

theory = scalingtheory.ScalingTheory(fvars, fvars['independent'],\
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

exec(thisModule + "= SloppyScaling.Model(theory, data, name, WS.sortedValues)")
