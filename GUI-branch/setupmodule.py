import os, sys, pickle
import scalingtheory
import WindowScalingInfo as WS
from sloppyscaling import Data, Model
import getData
import scipy as sp

corrections_to_scaling = None
normalization = "normLog"
initialSkipIndex = 0 #Skip data when LOADING
initialSkipValue = 0.01 # P(Hc) - Lasse
#initialSkipValue = 2. # RfimDip
#initialSkipValue = 0 # Stefano


# Colors and shapes for data points for plots
# (shared between different data types)
def makeSymbolsAndColors():
    """
    Yield a Symbol and Color
    """
    # YJC: right now we have 128 different values, need to have more colors
    # which means we need to fix the 
    # 13 symbols, 7 colors: numbers should be relatively prime
    # 143 maximum different
    pointSymbolTypes = ['o','^','v','<','>','s','p','+','x','d','h','*','.']
    pointColorTypes = ['b','g','r','c','m','k','y']
    # Replicate to make enough symbols for different data types
    symbolList = len(pointColorTypes) * pointSymbolTypes
    colorList = len(pointSymbolTypes) * pointColorTypes
    for i in zip(symbolList, colorList):
        yield i
    

class Module():

    def __init__(self, functionName, independentValues):
        dirFunctions = 'functions'
        filePkl = ".".join([functionName,"pkl"])
        filePkl = os.path.join(dirFunctions, filePkl)
        try:
            F = open(filePkl, 'rb')
            fvars = pickle.load(F)
        except:
            print "There is an error in the file : "+ filePkl
            sys.exit()

        name = fvars['Yname'] # This is the name used in the files
        self.name = name.replace("__","")
        fvars['initialParameterValues'] = (1.12, 1.3,1.,0.1, 1.6, .75, 1.,50.0) # Lasse
        #fvars['initialParameterValues'] = (1.12, 1.3,3.,20., .6, .75,1e-2) # RFimDip        
        #fvars['initialParameterValues'] = (1.12, 1.3) # Stefano
        #fvars['initialParameterValues'] = (1.2, 1.3,.6,1.,50.0)
        fvars['deriv'] = fvars['derivNoCorrections']
        if corrections_to_scaling:
            fvars['Yvalue'] = fvars['Yvalue'] + fvars['Ysign'] + fvars['Ycorrections']
            fvars['initialParameterValues_corrections'] = (0.05, 0.2)
            fvars['parameterNames'] = fvars['parameterNames'] + "," + fvars['parameterNames_corrections']
            fvars['initialParameterValues'] = fvars['initialParameterValues'] + fvars['initialParameterValues_corrections']
            fvars['deriv'] = fvars['derivWithCorrections']
        
        self.independentNames = fvars['independentNames']
        self.theory = scalingtheory.ScalingTheory(fvars, normalization=normalization)
        self.data = Data()
        loaded = 0
        # Call the symb-color generator
        sc = makeSymbolsAndColors()
        for independent in independentValues:
            exec "%s = independent" % fvars['independentNames']
            fileName = independentValues[independent]
            symbol, color = sc.next()
            success = self.data.installCurve(independent, fileName, \
                                        pointSymbol=symbol, pointColor=color, \
                                        initialSkipIndex=initialSkipIndex, initialSkipValue=initialSkipValue)
            if normalization == 'normLog':
                lgX = sp.log10(self.data.X[independent])
                D = lgX[1] - lgX[0]
                bins = 10**(lgX+D/2.) - 10**(lgX-D/2.)
                self.theory.normFactor[independent] = sp.sum(bins*self.data.Y[independent])
            loaded += success
        nFiles = len(independentValues)
        if loaded ==  nFiles:
            self.loadedMsg = "Loaded %2d/%2d files (%s)" % (loaded, nFiles, name)
        else:
            self.loadedMsg = "Attention! %2d/%2d files are missing (%s)" %  (nFiles-loaded, nFiles, name)
            
        self.modelObject = Model(self.theory, self.data, self.name, WS.sortedValues)
        