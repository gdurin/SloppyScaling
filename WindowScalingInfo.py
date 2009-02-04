
"""
Useful information about the WindowScaling data sets
"""
import scipy

# Independent variables describing data.
independentNames = "k,L,win"
# Type of normalization for the function (None, NormBasic, NormIntegerSum)
normalization = "NormBasic"
# Decide to add corrections to scaling in the function module (True/False)
corrections_to_scaling = False
# Rows to skip in the dataFiles
rows_to_skip = 2

# System Size (used to get the fileNames) and
# values of independent variables. (List of tuples if more than one)
#systemSize = "2048x1024"
#independentValues = [0.001,0.005,0.01,0.05,0.1,1,10]
#systemSize = "4096x2048"
#independentValues = [0.001,0.005]
#systemSize = "8192x4096"
#independentValues = [0.0001,0.0005,0.001]
#independentValues without window sizes...
#independentValues = \
#  [(0.001,1024), (0.005,1024),(0.01,1024),(0.05,1024),(0.1,1024), \
#	(1,1024),(10,1024), \
#  	(0.001,2048),(0.005,2048), \
#  	(0.0001,4096),(0.001,4096),(0.005,4096)]
#independentValues with window sizes

#independentValues = [(0.001,1024,2), (0.005,1024,2),(0.01,1024,2),(0.05,1024,2),(0.1,1024,2),(1,1024,2),(10,1024,2)]

independentValues = [(0.01, 1024, 128),(0.05, 1024, 64),(10,1024,8),(0.001,4096,512),(0.005,4096,256)]

#independentValues = [(0.001,1024, 1),(0.001, 1024, 2), (0.001, 1024, 4), (0.001, 1024, 8), (0.001, 1024, 16), (0.001, 1024, 32), (0.001, 1024, 64), (0.001, 1024, 128), (0.001, 1024, 256),(0.001, 1024, 512),(0.005,1024, 1),(0.005, 1024, 2), (0.005, 1024, 4), (0.005, 1024, 8), (0.005, 1024, 16), (0.005, 1024, 32), (0.005, 1024, 64), (0.005, 1024, 128), (0.005, 1024, 256),(0.005, 1024, 512),(0.01,1024, 1),(0.01, 1024, 2), (0.01, 1024, 4), (0.01, 1024, 8), (0.01, 1024, 16), (0.01, 1024, 32), (0.01, 1024, 64), (0.01, 1024, 128), (0.01, 1024, 256),(0.01, 1024, 512),(0.05,1024, 1),(0.05, 1024, 2), (0.05, 1024, 4), (0.05, 1024, 8), (0.05, 1024, 16), (0.05, 1024, 32), (0.05, 1024, 64), (0.05, 1024, 128), (0.05, 1024, 256),(0.05, 1024, 512),(0.1,1024, 1),(0.1, 1024, 2), (0.1, 1024, 4), (0.1, 1024, 8),(0.1, 1024, 16), (0.1, 1024, 32), (0.1, 1024, 64), (0.1, 1024, 128), (0.1, 1024, 256),(0.1, 1024, 512),(1, 1024,1),(1, 1024, 2), (1, 1024, 4), (1, 1024, 8),(1, 1024, 16), (1, 1024, 32), (1, 1024, 64), (1, 1024, 128), (1, 1024, 256),(1, 1024, 512),(10, 1024, 1),(10, 1024, 2) ,(10, 1024, 4), (10, 1024, 8),(10, 1024, 16), (10, 1024, 32), (10, 1024, 64), (10, 1024, 128), (10, 1024, 256),(10, 1024, 512), (0.001, 2048, 2) ,(0.001, 2048, 4), (0.001, 2048, 8),(0.001, 2048, 16), (0.001, 2048, 32), (0.001, 2048, 64), (0.001, 2048, 128), (0.001, 2048, 256),(0.001, 2048, 512), (0.001, 2048, 1024),(0.005, 2048, 2) ,(0.005, 2048, 4), (0.005, 2048, 8),(0.005, 2048, 16), (0.005, 2048, 32), (0.005, 2048, 64), (0.005, 2048, 128), (0.005, 2048, 256),(0.005, 2048, 512), (0.005, 2048, 1024), (0.0001, 4096, 2) ,(0.0001, 4096, 4), (0.0001, 4096, 8),(0.0001, 4096, 16), (0.0001, 4096, 32), (0.0001, 4096, 64), (0.0001, 4096, 256),(0.0001, 4096, 512), (0.0001, 4096, 1024), (0.0001,4096, 2048),(0.001, 4096, 2) ,(0.001, 4096, 4), (0.001, 4096, 8),(0.001, 4096, 16), (0.001, 4096, 32), (0.001, 4096, 64), (0.001, 4096, 128), (0.001, 4096, 256),(0.001, 4096, 512), (0.001, 4096, 1024), (0.001,4096, 2048),(0.005, 4096, 2) ,(0.005, 4096, 4), (0.005, 4096, 8),(0.005, 4096, 16), (0.005, 4096, 32), (0.005, 4096, 64), (0.005, 4096, 128), (0.005, 4096, 256),(0.005, 4096, 512), (0.005, 4096, 1024), (0.005,4096, 2048)]

# Type of simulation: Linear, NonLinear etc
simulType = "NonLinear"

# Directory where data to be fit is stored
IthacaDataDirectory = "data/"
# XXX We put all the different files into the same directory???
# GianfrancoDataDirectory = "/home/meas/WinSim/NonLinear/L"+ systemSize + "/data/"
dataDirectory = IthacaDataDirectory

# Data to fit and models
#moduleNames = ['Ahk','Awk']
moduleNames = ['Ahk', 'A11', 'A00']

#
# DO NOT CHANGE ANYTHING BELOW
#
# Check if independentNames and moduleNames has a ',' at the end, and add it if needed
independentNames += (independentNames[-1]!=',') * ","
# XXX Changed JPS systemSize = "System_Size=" + systemSize


# Colors and shapes for data points for plots
# (shared between different data types)
def MakeSymbolsAndColors(independentValues):
    """
    Generate dictionaries Symbol[independent] and Color[independent]
    """
    # YJC: right now we have 128 different values, need to have more colors
    # which means we need to fix the 
    # 13 symbols, 7 colors: numbers should be relatively prime
    # 143 maximum different
    pointSymbolTypes = ['o','^','v','<','>','s','p','+','x','d','h','*','.','H']
    pointColorTypes = ['b','g','r','c','m','k','y']
    # Replicate to make enough symbols for different data types
    SymbolList = len(pointColorTypes) * pointSymbolTypes
    ColorList = len(pointSymbolTypes) * pointColorTypes
    Symbols = {}
    Colors = {}
    for n, independent in enumerate(independentValues):
        Symbols[independent] = SymbolList[scipy.mod(n, 9)]
        Colors[independent] = ColorList[scipy.mod(n, 7)]

    return Symbols, Colors

Symbol, Color = MakeSymbolsAndColors(independentValues)
