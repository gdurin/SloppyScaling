import sympy
from sympy import exp,log,ln,cos,sin,tan,tanh

def getDiff(variables,function,varsDiff):
    """
    This function makes the analytical derivative 
    of a  "function(variables)" over variable(s) "varsDiff"
    Example:
    f(x,y) = x**2+y**2
    variables = ["x","y"]
    function = "x**2+y**2"
    varDiff = "x"
    return 2*x
    varsDiff is a list
    return a list of the derivatives
    """
    diffs = []
    # There is a problem if varsDiff is not a list 
    # check and solve
    if type(varsDiff).__name__ == "str":
        varsDiff = [varsDiff]
    # Define all the variables as sympy.Symbols
    for v in variables:
        sympy.var(v)
    # Define the function "f"
    exec "f = %s" % (function)
    # Do the loop over the variables varsDiff
    for vD in varsDiff:
        exec "d = sympy.diff(f,%s)" % vD
        #d = sympy.simplify(d) TOO risky
        diffs.append(str(d))
    return diffs

if __name__ == '__main__':
    s = "(S*(k/L)**(sigma_k*zeta)/W)**((2.-tau)*(1.+zeta)/zeta)/S \
      * exp(-1.0*(S*(1.0*k/L)**(sigma_k*zeta)/W)**n*I__xh)"

    allVariables = "S,tau,zeta,sigma_k,n,I__xh,W,k,L".split(",")
    variablesDiff = "tau,zeta,sigma_k,n".split(",")
    diffs = getDiff(allVariables,s,variablesDiff)
    for i,d in enumerate(diffs):
        print "ds/d(%s) = %s" % (variablesDiff[i], d)