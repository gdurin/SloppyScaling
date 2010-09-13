import numexpr as ne
from numpy import exp

class ScalingTheory:
    """
    A ScalingTheory's job is to provide a function Y(X) that predicts
    theory for an experiment, given a set of independent variables and
    parameters. The independent variables are those specifying the Data
    being described; the parameters describe universal critical
    exponents, universal scaling functions, and analytic
    and singular corrections to scaling.
    The theory is represented in a string consisting of a Python command.
    The variables are unpacked on the fly and the string is executed...
    For application convenience, you may use the natural variables for
    X and Y (say, 'S' and 'A') in the expressions, and set Xname and Yname
    appropriately.
    #
    Example of implementation:
    sizeHisto = ScalingTheory(TODO)
    """
    def __init__(self, fvars, independentNames, \
                 heldParameterBool = False, heldParameterList = "", heldParameterPass = False,\
                 normalization = None):
        for key in fvars:
            setattr(self,key,fvars[key])
            print key
        print self.initialParameterValues
        self.parameterNameList = self.parameterNames.split(",")
        self.parameterNames0 = self.parameterNames 
        self.parameterNameList0 = self.parameterNameList
        self.initialParameterValues0 = self.initialParameterValues
        self.independentNames = independentNames
        self.normalization = normalization
        self.heldParameterBool = heldParameterBool
        self.heldParameterPass = heldParameterPass

    def Y(self, X, parameterValues, independentValues):
        """
        Predicts Y as a function of X
        """
        # Set values of parameters based on vector of current guess
        # Set values of independent variables based on which curve is being fit
        # Set up vector of independent variable from X
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        exec(self.parameterNames + " = parameterValues")
        exec(self.independentNames + " = independentValues")
        if self.heldParameterBool:
            for par, val in self.heldParameterList:
                exec(par + " = " + str(val))
        exec(self.Xname + ' = X')
        if self.XscaledName:
            exec(self.XscaledName +'='+ self.XscaledValue)
        #YJC: added scalingW here
        if self.WscaledValue:
            exec(self.WscaledName +"="+ self.WscaledValue)
        #exec("Y = " + self.Yvalue)
        Y = ne.evaluate(self.Yvalue)
        if self.normalization:
            fn = getattr(self, self.normalization)
            Y = fn(X, Y, parameterValues, independentValues)
        return Y

    def ScaleX(self, X, parameterValues, independentValues):
        """
        Rescales X according to scaling form
        """
        # Set values of parameters, independent variables, and X vector
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        exec(self.parameterNames + " = parameterValues")
        exec(self.independentNames + " = independentValues")
        if self.heldParameterBool:
            for par, val in self.heldParameterList:
                exec(par + " = " + str(val))
        exec(self.Xname + " = X")
        #YJC: added scalingW here too
        if self.WscaledValue is not None:
            exec(self.WscaledName + '=' +self.WscaledValue)
        #exec("XScale = " + self.XscaledValue)
        return ne.evaluate(self.XscaledValue)

    def ScaleY(self, X, Y, parameterValues, independentValues):
        """
        Rescales Y according to form
        """
        # Set values of parameters, independent variables, and X vector
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        exec(self.parameterNames + " = parameterValues")
        exec(self.independentNames + " = independentValues")
        if self.heldParameterBool:
            for par, val in self.heldParameterList:
                exec(par + " = " + str(val))
        exec(self.Xname + " = X")
        #YJC: added scalingW here too
        if self.WscaledValue is not None:
            exec(self.WscaledName + '=' +self.WscaledValue)
        if self.XscaledName:
            exec(self.XscaledName + "="+self.XscaledValue)
        exec(self.Yname + " = Y")
        #exec("YScale = " + self.YscaledValue)
        return ne.evaluate(self.YscaledValue)

    def reduceParameters(self,pNames,pValues,heldParams):
        list_params = pNames.split(",")
        list_initials = list(pValues)
        for param_to_remove, val in heldParams:
            try:
                index = list_params.index(param_to_remove)
                list_params.pop(index)
                list_initials.pop(index)
            except ValueError:
                print "Warning: parameter ", param_to_remove, " NOT included in the list"
        return ",".join(list_params), tuple(list_initials)

    def HoldFixedParams(self, heldParameters):
        """
        Sets parameters to fixed values.
        heldParameters is a list of tuple(s) of the type:
        [('param1', val1), ('param2', val2)]
        """
        
        if heldParameters:
            self.heldParameterBool = True
            pNames, pValues = \
                    self.reduceParameters(self.parameterNames0, \
                                           self.initialParameterValues0, \
                                           heldParameters)
            self.parameterNames = pNames
            self.parameterNameList = pNames.split(",")
            self.initialParameterValues = pValues
            self.heldParameterList = heldParameters
            self.heldParameterBool = True
            self.heldParameterPass = True
        else:
            # Check if some parameters have been held before, and reset
            if self.heldParameterPass:
                self.parameterNames=self.parameterNames0
                self.parameterNameList = self.parameterNameList0
                self.initialParameterValues = self.initialParameterValues0
                self.heldParameterBool = False
                self.heldParameterList = None
                
    #
    # Various options for normalization
    #
    def NormBasic(self, X, Y, parameterValues, independentValues):
        """
        Must guess at bin sizes for first and last bins
        """
        norm = Y[0]*(X[1]-X[0])
        norm += sum(Y[1:-1] * (X[2:]-X[:-2])/2.0)
        # GF: Why not this below?
        #norm += sum(Y[1:-2] * (X[2:-1]-X[:-3])/2.0)
        norm += Y[-1]*(X[-1]-X[-2])
        return Y/norm
    
    def NormIntegerSum(self, X, Y, parameterValues, independentValues, \
                xStart=1., xEnd=1024.):
        """
        Function summed over positive integers equals one; brute force
        up to xEnd
        """
        x = scipy.arange(xStart, xEnd)
        return Y/sum(self.Y(x, parameterValues, independentValues))
        
    def NormLog(self,X,Y,parameterValues, independentValues):
        """
        This kind of normalization is correct
        if the data are uniform in log scale,
        as prepared by our code toBinDistributions.py
        """
        lgX = scipy.log10(X)
        D = scipy.around(lgX[1] - lgX[0],2)
        bins = 10**(lgX+D/2.) - 10**(lgX-D/2.)
        return Y/sum(Y*bins)
