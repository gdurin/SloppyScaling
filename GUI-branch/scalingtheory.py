from __future__ import division
import numexpr as ne
from numpy import exp, empty
import scipy

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
    sizeHisto = ScalingTheory(still TODO)
    """
    def __init__(self, fvars, normalization=None):
        for key in fvars:
            setattr(self,key,fvars[key])
            #print key,": ", fvars[key]
            #print 
        self.parameterNameList = self.parameterNames.split(",")
        self.parameterNames0 = self.parameterNames 
        self.parameterNameList0 = self.parameterNameList
        self.initialParameterValues0 = self.initialParameterValues
        self.normalization = normalization
        self.isHeldParameter = False
        self.heldParameterPass = False
        self.numIndepParameters = len(fvars['independentNames'].split(","))
        self.normFactor = {}
        self.norm = {}


    def Y(self, X, parameterValues, independentValues):
        """
        Predicts Y as a function of X
        """
        # Set values of parameters based on vector of current guess
        # Set values of independent variables based on which curve is being fit
        # Set up vector of independent variable from X
        exec  "%s = parameterValues" % self.parameterNames
        if self.numIndepParameters == 1:
            exec  "%s, = independentValues" % self.independentNames
        else:
            exec  "%s = independentValues" % self.independentNames
            
        if self.isHeldParameter:
            for par, val in self.heldParameterList:
                exec "%s = %s" % (par,str(val))
        exec  "%s = X" % self.Xname
        if self.XscaledName:
            exec "%s = %s" % (self.XscaledName, self.XscaledValue)
        if self.WscaledValue:
            exec "%s = %s" % (self.WscaledName, self.WscaledValue)
        Y = ne.evaluate(self.Yvalue)
        if self.normalization:
            fn = getattr(self, self.normalization)
            normFactor = fn(X, Y, parameterValues, independentValues)
            self.norm[independentValues] = normFactor
        return Y*normFactor

    def ScaleX(self, X, parameterValues, independentValues):
        """
        Rescales X according to scaling form
        """
        # Set values of parameters, independent variables, and X vector
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        exec  "%s = parameterValues" % self.parameterNames
        if self.numIndepParameters == 1:
            exec  "%s, = independentValues" % self.independentNames
        else:
            exec  "%s = independentValues" % self.independentNames
        if self.isHeldParameter:
            for par, val in self.heldParameterList:
                exec "%s = %s" % (par,str(val))
        exec  '%s = X' % self.Xname
        if self.WscaledValue:
            exec "%s = %s" % (self.WscaledName, self.WscaledValue)
        return ne.evaluate(self.XscaledValue)

    def ScaleY(self, X, Y, parameterValues, independentValues):
        """
        Rescales Y according to form
        """
        # Set values of parameters, independent variables, and X vector
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        #independentValues = tuple(map(float,independentValues))
        exec  "%s = parameterValues" % self.parameterNames
        if self.numIndepParameters == 1:
            exec  "%s, = independentValues" % self.independentNames
        else:
            exec  "%s = independentValues" % self.independentNames
        if self.isHeldParameter:
            for par, val in self.heldParameterList:
                exec "%s = %s" % (par,str(val))
        exec  '%s = X' % self.Xname
        if self.XscaledName:
            exec "%s = %s" % (self.XscaledName, self.XscaledValue)
        if self.WscaledValue:
            exec "%s = %s" % (self.WscaledName, self.WscaledValue)
        exec  "%s = Y" % self.Yname
        return ne.evaluate(self.YscaledValue)/self.norm[independentValues]

    def reduceParameters(self,pNames,pValues,heldParams):
        list_params = pNames.split(",")
        list_initials = list(pValues)
        for paramToRemove, val in heldParams:
            try:
                index = list_params.index(paramToRemove)
                list_params.pop(index)
                list_initials.pop(index)
            except ValueError:
                print "Warning: parameter ", param_to_remove, " NOT included in the list"
        return ",".join(list_params), tuple(list_initials)

    def jacobian(self,X,Y,parameterValues,independentValues):
        """
        Calculate the jacobian using analytical derivatives
        """
        exec "%s = parameterValues" % self.parameterNames
        if self.numIndepParameters == 1:
            exec  "%s, = independentValues" % self.independentNames
        else:
            exec  "%s = independentValues" % self.independentNames
        exec "%s = X" % self.Xname
        if self.isHeldParameter:
            for par, val in self.heldParameterList:
                exec "%s = %s" % (par, str(val))
        D = []
        for param in self.parameterNameList:
            D.append(self.deriv[param])
        jb = scipy.array(map(ne.evaluate,D))
        return jb*self.norm[independentValues]
        
        
    def holdFixedParams(self, heldParameters):
        """
        Sets parameters to fixed values.
        heldParameters is a list of tuple(s) of the type:
        [('param1', val1), ('param2', val2)]
        """
        
        if heldParameters:
            self.isHeldParameter = True
            self.parameterNames, self.initialParameterValues = \
                    self.reduceParameters(self.parameterNames0, \
                                           self.initialParameterValues0, \
                                           heldParameters)
            self.parameterNameList = self.parameterNames.split(",")
            self.heldParameterList = heldParameters
            self.isHeldParameter = True
            self.heldParameterPass = True
        else:
            # Check if some parameters have been held before, and reset
            if self.heldParameterPass:
                self.parameterNames=self.parameterNames0
                self.parameterNameList = self.parameterNameList0
                self.initialParameterValues = self.initialParameterValues0
                self.isHeldParameter = False
                self.heldParameterList = None
            
    #
    # Various options for normalization
    #
    
    def normBasic(self, X, Y, parameterValues, independentValues):
        """
        Must guess at bin sizes for first and last bins
        """
        norm = Y[0]*(X[1]-X[0])
        norm += sum(Y[1:-1] * (X[2:]-X[:-2])/2.0)
        # GF: Why not this below?
        #norm += sum(Y[1:-2] * (X[2:-1]-X[:-3])/2.0)
        norm += Y[-1]*(X[-1]-X[-2])
        return Y/norm
    
    def normIntegerSum(self, X, Y, parameterValues, independentValues):
        """
        Function summed over positive integers equals one; brute force
        up to xEnd
        """
        xMax = X[-1]+1
        print xMax
        x = scipy.arange(1, xMax)
        return Y/sum(self.Y(x, parameterValues, independentValues))
        
    def normLog(self,X,Y,parameterValues, independentValues):
        """
        Output: give the correct normalization factor 
        for data in uniform in log scale,
        """
        lgX = scipy.log10(X)
        D = lgX[1] - lgX[0]
        bins = 10**(lgX+D/2.) - 10**(lgX-D/2.)
        return self.normFactor[independentValues] / scipy.sum(Y*bins)
        
    def normLogNotUniform(self,X,Y,parameterValues, independentValues):
        """
        Normalization for data non-uniform in log scale;
        uses a and delta as chosen by Lasse
        """
        a = 1.4
        d = 1.4
        bins = [a**n*d for n in range(len(X))]
        return Y/sum(Y*bins)

    def normSum(self,X,Y,parameterValues, independentValues):        
        return Y/self.normFactor[independentValues]