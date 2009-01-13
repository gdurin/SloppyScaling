
"""
Useful information about the WindowScaling data sets
"""

# Directory where data to be fit is stored
IthacaDataDirectory = "data/"
GianfrancoDataDirectory = "/home/meas/WinSim/NonLinear/L1024x2048/data/"
dataDirectory = GianfrancoDataDirectory

# Independent variables describing data.
independentNames = "k"
# Values for independent variables. (List of tuples if more than one.)
independentValues = [0.001,0.005,0.01,0.05,0.1,1,10]
# Type of normalization for the function (None, NormBasic, NormIntegerSum)
normalization = "NormBasic"

#
# DO NOT CHANGE ANYTHING BELOW
#
# Check if independentNames has a ',' at the end, and add it if needed
independentNames += (independentNames[-1]!=',') * ","

# Colors and shapes for data points for plots
# (shared between different data types)
def MakeSymbolsAndColors(independentValues):
    """
    Generate dictionaries Symbol[independent] and Color[independent]
    """
    # 9 symbols, 5 colors: numbers should be relatively prime
    # 45 maximum different
    pointSymbolTypes = ['o','^','v','<','>','s','p','+','x']
    pointColorTypes = ['b','g','r','c','m']
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
