import scipy

def get_independent(MyList, sorting = False, sigma = 0.387):
    """
    Calculate the tuple of (L,k) or (L,k,W)
    using a List written in short form, as follows:
    [\
    [L,[k1,k2,k3,...],[W1,W2]]\ Case 1    
    [L,[k1,k2,k3,...],(Wmin,Wmax)]\ Case 2
    ...\
    ]
    The Windows W of Case 2 are calculated as powers of 2,
    from Wmin to Wmax included
    Output:
    independentNames (as "L,k", or "L,k,W")
    independentValues
    """
    out = {}
    numIndependentNames = len(MyList[0])
    independentNames = "L, k"
    if numIndependentNames == 3:
        independentNames = independentNames + ", W"
    #
    for line in MyList:
        if numIndependentNames == 2:
            L, ks = line
        elif numIndependentNames == 3:
            L, ks, Ws = line
            if isinstance(Ws,int):
                Ws = [Ws]
            elif isinstance(Ws,tuple):
                lower_e, upper_e = scipy.log2(Ws[0]), scipy.log2(Ws[1])
                e2 = scipy.array(range(lower_e, upper_e+1))
                Ws = 2**e2
        if not isinstance(ks,list):
            ks = [ks]
        
        for k in ks:
            if numIndependentNames == 2:
                wincorr = 1.0*k/L
                out[wincorr] = L, k
            elif numIndependentNames == 3:
                for W in Ws:
                    wincorr = 1.0*W*(1.0*k/L)**sigma
                    out[wincorr] = L, k, W

    if sorting:
        return independentNames, map(out.get,sorted(out))
    else:
        return independentNames, out.values()

def reduceParameters(pNames,pValues,fixedParams):
    list_params = pNames.split(",")
    list_initials = list(pValues)
    for param_to_remove, val in fixedParams:
        try:
            index = list_params.index(param_to_remove)
            list_params.pop(index)
            list_initials.pop(index)
        except ValueError:
            print "Warning: parameter ", param_to_remove, " NOT included in the list"
    return ",".join(list_params), tuple(list_initials)

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
    pointSymbolTypes = ['o','^','v','<','>','s','p','+','x','d','h','*','.']
    pointColorTypes = ['b','g','r','c','m','k','y']
    # Replicate to make enough symbols for different data types
    SymbolList = len(pointColorTypes) * pointSymbolTypes
    ColorList = len(pointSymbolTypes) * pointColorTypes
    Symbols = {}
    Colors = {}
    for n, independent in enumerate(independentValues):
        Symbols[independent] = SymbolList[scipy.mod(n, 13)]
        Colors[independent] = ColorList[scipy.mod(n, 7)]
    return Symbols, Colors