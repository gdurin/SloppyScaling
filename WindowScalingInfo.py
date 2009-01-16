
"""
Useful information about the WindowScaling data sets
"""

# System Size (used to get the fileNames)
systemSize = "2048x1024"
#systemSize = "4096x2048"
#systemSize = "8192x4096"

# Type of simulation: Linear, NonLinear etc
simulType = "NonLinear"

# Directory where data to be fit is stored
IthacaDataDirectory = "data/"
GianfrancoDataDirectory = "/home/meas/WinSim/NonLinear/L"+ systemSize + "/data/"
dataDirectory = GianfrancoDataDirectory

# Data to fit and models
#moduleNames = ['Ahk','Awk']
moduleNames = ['Ahk']

# Independent variables describing data.
independentNames = "k"
# Values for independent variables. (List of tuples if more than one.)
#independentValues = [0.001,0.005,0.01,0.05,0.1,1,10]
independentValues = [0.005,0.01,0.05,0.1,1,10]
# Type of normalization for the function (None, NormBasic, NormIntegerSum)
normalization = "NormBasic"
# Decide to add corrections to scaling in the function module (True/False)
corrections_to_scaling = False
# Rows to skip in the dataFiles
rows_to_skip = 2
#
# DO NOT CHANGE ANYTHING BELOW
#
# Check if independentNames and moduleNames has a ',' at the end, and add it if needed
independentNames += (independentNames[-1]!=',') * ","
systemSize = "System_Size=" + systemSize


# Colors and shapes for data points for plots
# (shared between different data types)
def MakeSymbolsAndColors(independentValues):
    """
    Generate dictionaries Symbol[independent] and Color[independent]
    """
    # 9 symbols, 5 colors: numbers should be relatively prime
    # 45 maximum different
    pointSymbolTypes = ['o','^','v','<','>','s','p','+','x']
    pointColorTypes = ['b','g','r','c','m','k','y']
    # Replicate to make enough symbols for different data types
    SymbolList = len(pointColorTypes) * pointSymbolTypes
    ColorList = len(pointSymbolTypes) * pointColorTypes
    Symbols = {}
    Colors = {}
    for n, independent in enumerate(independentValues):
        Symbols[independent] = SymbolList[n]
        Colors[independent] = ColorList[n]

    return Symbols, Colors

Symbol, Color = MakeSymbolsAndColors(independentValues)
