import glob

def getFunctionNames(subDir='functions'):
    """
    get a dictionary where the keys 
    are the function names of defined functions 
    and contains the whole pathname
    """
    functionDict = {}
    getPklFileNames = glob.glob(subDir+"/*.pkl")
    for el in getPklFileNames:
        function = el.split("/")[-1].split(".pkl")[0]
        functionDict[function] = el
    return functionDict
