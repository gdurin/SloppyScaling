import scipy
import pylab
import copy
from scipy import exp
import scipy.optimize
import scipy.special
import WindowScalingInfo as WS
reload(WS)



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
    sizeHisto = ScalingTheory('S**(-tau)*scipy.exp((-(S*(R-Rc)**sigma)/XS)**nS)',
                'tau, sigma, XS, nS, Rc', (1.5,0.5,1.0,1.0,2.0),
                independentNames = 'R',
                scalingX = 'S*r**sigma', scalingY = 'D*S**tau',
                scalingXTeX = r'$S r^\sigma$',
                scalingYTeX = r'$D S^\tau$',
                title= 'Avalanche histo$'
                scalingTitle= 'Avalanche histo scaling plot'
                Xname = 'S', XscaledName='Ss', Yname = 'D', normalization = True)
    """
    def __init__(self, Ytheory, parameterNames, initialParameterValues, \
                 independentNames, \
                 scalingX = 'X', scalingY = 'Y', scalingW = None, \
                 scalingXTeX = r'${\cal{X}}$', \
                 scalingYTeX = r'${\cal{Y}}$', \
                 title = 'Fit', scalingTitle = 'Scaling Collapse',
                 Xname='X', XscaledName = 'Xs', Yname='Y', WscaledName = 'Ws',\
                 heldParameterBool = False, heldParameterList = "", heldParameterPass = False,
                 normalization = None):
        #YJC: added WscaledName = 'Ws' and scalingW =None to theory
        # to make the scaling function easier to read, need to keep default none for scalingW,
        #because some theories don't have this second variable
        #YJC: want to make the scaling variables a list?  So we can specify as many as we want
        self.Ytheory = Ytheory
        self.parameterNames = parameterNames
        self.parameterNameList = parameterNames.split(",")
        self.initialParameterValues = initialParameterValues
        self.parameterNames0 = parameterNames 
        self.parameterNameList0 = self.parameterNameList
        self.initialParameterValues0 = initialParameterValues
        self.independentNames = independentNames
        self.Xname = Xname
        self.XscaledName = XscaledName
        self.Yname = Yname
        self.WscaledName = WscaledName
        self.scalingX = scalingX
        self.scalingY = scalingY
        self.scalingW = scalingW
        self.scalingXTeX = scalingXTeX
        self.scalingYTeX = scalingYTeX
        self.title = title
        self.scalingTitle = scalingTitle
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
            exec(self.XscaledName +'='+ self.scalingX)
        #YJC: added scalingW here
        if self.scalingW:
            exec(self.WscaledName +"="+ self.scalingW)
        exec("Y = " + self.Ytheory)
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
        if self.scalingW is not None:
            exec(self.WscaledName + '=' +self.scalingW)
        exec("XScale = " + self.scalingX)
        return XScale

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
        if self.scalingW is not None:
            exec(self.WscaledName + '=' +self.scalingW)
        if self.XscaledName:
            exec(self.XscaledName + "="+self.scalingX)
        exec(self.Yname + " = Y")
        exec("YScale = " + self.scalingY)
        return YScale

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

class Data:
    """
    A Data object contains a series of curves each for a set of independent
    control parameters. For example, the X values might be avalanche sizes
    (Xname = 'S'), the Y values might be percentage area covered by
    avalalanches of that size (Yname = 'A'),
    the sigmas the standard errors in the means, and an independent control
    parameters might be the demagnetizing field (independent = 'k'). If,
    as for A(S), the data plots are typically log-log set self.linlog = 'log';
    for things like V(t,T) set self.linlog = 'lin'.
    """ 
    def __init__(self, linlog = 'log'):
        self.experiments = []
        self.X = {}
        self.Y = {}
        self.linlog = linlog
        self.pointType = {}
        self.errorBar = {}
        self.fileNames = {}
        self.defaultFractionalError = {}
        self.initialSkip = {}
        
    def InstallCurve(self, independent, fileName, defaultFractionalError = 0.1,\
                     pointSymbol="o", pointColor="b", \
                     xCol=0, yCol=1, errorCol = 2, initialSkip = 0, factorError = 10.0):
        """
        Curves for independent control parameters given by "independent"
        loaded from "fileName". Plots use, for example, pointSymbol from 
            ['o','^','v','<','>','s', 'p', 'h','+','x']
        and pointColor from 
            ['b','g','r','c','m','burlywood','chartreuse']
        
        factorError is to artificially increase error bars for better fits
        """
        
        # check if independent is a tuple
        if not isinstance(independent, tuple):
            print "Warning: the independent variable is not a tuple"
            independent = tuple(independent)
        #
        self.experiments.append(independent)
        self.fileNames[independent] = fileName
        self.initialSkip[independent] = initialSkip
        self.pointType[independent] = pointColor + pointSymbol
        self.defaultFractionalError[independent] = defaultFractionalError
        try:
            infile = open(fileName, 'r')
            lines = infile.readlines()
            infile.close()
            success = 1
            numbers = [line.split() for line in lines]
            self.X[independent] = scipy.array( \
                        [float(line[xCol]) for line in numbers])
            self.Y[independent] = scipy.array( \
                        [float(line[yCol]) for line in numbers])
            if not errorCol:
                self.errorBar[independent] =  \
                        scipy.array([float(line[errorCol])*factorError for line in numbers])
            else:
                self.errorBar[independent] = \
                    self.Y[independent] * defaultFractionalError
        except IOError:
            print "File %s not found"%fileName
            success = 0
        return success

class Model:
    """
    A Model object unites Theory with Data. It's primary task is to 
    calculate the residuals (the difference between theory and data)
    and the cost.
    """
    def __init__(self, theory, data, name, sorting):
        self.theory = theory
        self.data = data
        self.name = name
        self.sorting = sorting
        
    def Residual(self, parameterValues, dictResidual=False):
        """
        Calculate the weighted residuals,
        with the weights = 1 / errorbar
        """
        if dictResidual:
            residuals = {}
        else:
            residuals = scipy.array([])
            
        for independentValues in self.data.experiments:
            initialSkip = self.data.initialSkip[independentValues]
            X = self.data.X[independentValues][initialSkip:]
            Y = self.data.Y[independentValues][initialSkip:]
            errorBar = self.data.errorBar[independentValues][initialSkip:]
            Ytheory = self.theory.Y(X, parameterValues, independentValues)
            # XXX Likely a better way to merge scipy arrays into big one
            # Yes: there is
            res = (Ytheory-Y)/errorBar
            if dictResidual:
                residuals[independentValues] = res
            else:
                residuals = scipy.concatenate((residuals,res))
        return residuals
        
    def Cost(self, parameterValues=None):
        """
        Sum of the squares of the residuals
        """
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        residuals = self.Residual(parameterValues)
        return sum(residuals*residuals)
    
    def SST(self, parameterValues=None):
        """
        SST is the sum of the squares about the mean
        """
        sst = 0.
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        for independentValues in self.data.experiments:
            initialSkip = self.data.initialSkip[independentValues]
            Y = self.data.Y[independentValues][initialSkip:]
            errorBar = self.data.errorBar[independentValues][initialSkip:]
            sst_partial = (Y-scipy.mean(Y))/errorBar
            sst += sum(sst_partial*sst_partial)
        return sst
    
    def R_square(self,parameterValues=None):
        """
        Calculates the R-square = 1 - cost / SST
        where SST is the sum of the squares about the mean
        """
        sst = self.SST(parameterValues)
        cost = self.Cost(parameterValues)
        return 1.- cost/sst
        
    def getLabel(self, names, values, withRescale = False, sigma = 0.387):
        """
        Get the Labels to be plotted. 
        """
        #lb_name = (names[-1] ==  ',') and names[:-1] or names[-1]
        lb = names + " = "
        lb += ",".join([str(i) for i in values])
        
        if withRescale:
            for nm, val in zip(a,b):
                exec(nm + "= " + str(val))
            if len(values) == 2:
                lb += str(1.0*k/L)
            elif len(values) == 3:
                lb += str((1.0*k/L)**sigma*W)[0:5]
        return lb
    
    def getAxis(self,X,Y):
        """
        return the proper axis limits for the plots
        """
        out = []
        mM = [(min(X),max(X)),(min(Y),max(Y))]
        for i,j in mM:
            #YJC: checking if values are negative, if yes, return 0 and break
            if j <0 or i <0:
                return 0
            log_i = scipy.log10(i)
            d, I = scipy.modf(log_i)
            if log_i < 0:
                add = 0.5 *(scipy.absolute(d)<0.5)
            else:
                add = 0.5 *(scipy.absolute(d)>0.5)
            m = scipy.floor(log_i) + add
            out.append(10**m)
            log_j = scipy.log10(j)
            d, I = scipy.modf(log_j)
            if log_j < 0:
                add = - 0.5 *(scipy.absolute(d)>0.5)
            else:
                add = - 0.5 *(scipy.absolute(d)<0.5)
            m = scipy.ceil(log_j) + add
            out.append(10**m)
        return tuple(out)
        
    def PlotFunctions(self, parameterValues=None, plotCollapse = False, 
                fontSizeLabels = 18, fontSizeLegend=12, pylabLegendLoc=(0.,0.)):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        # XXX Having problems with pylab.ioff()
        pylab.ioff()
        pylab.clf()
        ax0 = [1.e99,0,1.e99,0]
        if self.data.linlog == 'log':
            minY = 1.e99
            for independentValues in self.data.experiments:
                Y = self.data.Y[independentValues]
                if plotCollapse:
                    X = self.data.X[independentValues]
                    Y = self.theory.ScaleY(X,Y,parameterValues,\
                                           independentValues)
                minY = min(minY,min(Y))
        
        #pylab.plot([],label=r'$win (k/L)^{\sigma_k \zeta}$')
        
        if self.sorting:
            # preserve order of values as provided
            # by Utils.get_independent
            data_experiments = self.data.experiments
        else:
            # set sorted 
            data_experiments = sorted(self.data.experiments)
            
        for independentValues in data_experiments:
            X = self.data.X[independentValues]
            Y = self.data.Y[independentValues]
            Ytheory = self.theory.Y(X, parameterValues, independentValues)
            pointType = self.data.pointType[independentValues]
            errorBar = self.data.errorBar[independentValues]
            if plotCollapse:
                # Scaled error bars and Y need not-rescaled X
                errorBar = self.theory.ScaleY(X, errorBar, parameterValues, \
                                              independentValues)
                Y = self.theory.ScaleY(X, Y, parameterValues, independentValues)
                Ytheory = self.theory.ScaleY(X, Ytheory, \
                                             parameterValues, independentValues)
                # Then rescale X too
                X = self.theory.ScaleX(X, parameterValues, independentValues)
                
            # Avoid error bars crossing zero on log-log plots
            if self.data.linlog == 'log':
                errorBarDown = errorBar * (errorBar < Y) + (Y -minY) * (errorBar > Y)
                y_error=[errorBarDown,errorBar]
            else:
                y_error=errorBar
                
            # Prepare the labels
            lb = self.getLabel(self.theory.independentNames, independentValues)
            pylab.rcParams.update({'legend.fontsize':fontSizeLabels})
            #####################
            if self.data.linlog == 'log' or self.data.linlog == 'lin':
                if self.data.linlog == 'log':
                    plot_fn = getattr(pylab,'loglog')
                elif self.data.linlog == 'lin':
                    plot_fn = getattr(pylab,'plot')
                # Plot first data with their error
                plot_fn(X,Y,pointType[1])
                pylab.errorbar(X,Y, yerr=y_error, fmt=pointType,label=lb)
                axis_dep = self.getAxis(X,Y)
                # Get the current values of the axis
                # YJC: some values of binned data are negative, modified getAxis to check, and return 0 if negative values encountered 
                if axis_dep ==0:
                    print "this data set has negative values", independentValues
                    print "\n"
                for i, Ax in enumerate(axis_dep):
                    ax0[i] = i%2 and max(ax0[i],Ax) or min(ax0[i],Ax)
                # Plot the theory function
                plot_fn(X,Ytheory,pointType[0])
            else:
                print "Format " + self.data.linlog + \
                        " not supported yet in PlotFits"
                
        pylab.axis(tuple(ax0))
        pylab.legend(loc=pylabLegendLoc, ncol=2)
        #pylab.legend(loc=pylabLegendLoc)
        if plotCollapse:
            pylab.xlabel(self.theory.scalingXTeX, fontsize=fontSizeLabels)
            pylab.ylabel(self.theory.scalingYTeX, fontsize=fontSizeLabels)
            pylab.title(self.theory.scalingTitle)
        else:
            pylab.xlabel(self.theory.Xname, fontsize=fontSizeLabels)
            pylab.ylabel(self.theory.Yname, fontsize=fontSizeLabels)
            pylab.title(self.theory.title, fontsize=fontSizeLabels)
        # XXX Turn on if ioff used pylab.ion()
        pylab.ion()
        pylab.show()
        
    def PlotResiduals(self, parameterValues=None, \
                      fontSizeLabels = 18, pylabLegendLoc=(0.2,0.)):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        pylab.ioff()
        pylab.clf()
        residuals = self.Residual(parameterValues, dictResidual=True)
        x0 = 0
        for independentValues in sorted(residuals):
            res = residuals[independentValues]
            xStep = len(res)
            x = range(x0,x0+xStep)
            x0 += xStep
            pointType = self.data.pointType[independentValues]
            lb = self.getLabel(self.theory.independentNames, independentValues)
            pylab.plot(x,res,pointType, label=lb)
        pylab.ylabel("Weighted residuals")
        pylab.axhline(y=0,color='k')
        pylab.legend(loc=pylabLegendLoc)
        pylab.ion()
        pylab.show()
        
    def BestFit(self,initialParameterValues = None):
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues
        out = scipy.optimize.minpack.leastsq(self.Residual, \
                initialParameterValues, full_output=1, ftol=1.e-16) 
        return out
    
    def PlotBestFit(self, initialParameterValues = None, \
                    figFit = 1, figCollapse=2, fontSizeLabels=18, heldParams = None):
        
        #YJC: added abilitiy to set fixedParams for this, and also modified output to match what is done in composite theory

        if heldParams:
            if not isinstance(heldParams, list):
                heldParams=[heldParams]
            #Check now if the name is correct
            l_index=[]
            for index, par in enumerate(heldParams):
                pName, pValue = par
                if pName not in self.theory.parameterNameList0:
                    print "%s is not a valid name. Ignored" %pName
                    l_index.append(index)
            if l_index:
                for i in l_index:
                    heldParams.pop(i)

        # Call setHeldParams even if heldParams=None to 
        # check if original Names and values have to be used

        self.theory.HoldFixedParams(heldParams)
   
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues
        
        print 'initial cost = ', self.Cost(initialParameterValues)
        optimizedParameterValues = self.BestFit(initialParameterValues)[0]
        covar = self.BestFit(initialParameterValues)[1]
        errors = [covar[i,i]**0.5 for i in range(len(covar))]
        print 'optimized cost = ', self.Cost(optimizedParameterValues)
        print 'R-value = ', self.R_square(optimizedParameterValues)
        
        if heldParams:
            print "====== Held Parameters ======"
            for pName, pValue in heldParams:
                print "%s = %2.2f" %(pName, pValue)

        print "====== Fitted Parameters (with one sigma error) ======"
        for name, val, error in \
                zip(self.theory.parameterNameList,optimizedParameterValues, errors):
            print name + "= %2.4f +/- %2.4f" %(val, error)
        print "======================================================"

        pylab.figure(figFit)
        self.PlotFunctions(optimizedParameterValues)
        pylab.figure(figCollapse)
        self.PlotFunctions(optimizedParameterValues, plotCollapse = True)        
        #YJC: need to call these twice to show figures properly
        pylab.figure(figFit)
        pylab.figure(figCollapse)
        return optimizedParameterValues

class CompositeModel:
    """
    Class combining several Models into one
    The main job of CompositeModel is to combine the parameter lists and
    initial values into a single structure, and then to impose that structure
    on the individual theories.
    Also, plots and stuff should be delegated to the individual theories.
    """
    class CompositeTheory:
        def __init__(self):
            self.parameterNames = ""
            self.initialParameterValues = []
            self.parameterNameList = []
            
    def __init__(self, name):
        self.Models = {}
        self.theory = self.CompositeTheory()
        self.name = name
        self.heldParamsPass = False
        
    def InstallModel(self,modelName, model):
        self.Models[modelName] = model
        th = self.theory
        for param, init in zip(model.theory.parameterNameList, \
                                model.theory.initialParameterValues):
            if param not in th.parameterNameList:
                th.parameterNameList.append(param)
                th.initialParameterValues.append(init)
            else:
                # Check if shared param has consistent initial value
                # between models
                paramCurrentIndex = th.parameterNameList.index(param)
                paramCurrentInitialValue = \
                        th.initialParameterValues[paramCurrentIndex]
                if paramCurrentInitialValue != init:
                    print "Initial value %f"%(init,) \
                     + " for parameter " + param + " in model " + modelName \
                     + " \n disagrees with value %f"%(paramCurrentInitialValue)\
                     + " already stored for previous theory in " \
                     + " CompositeTheory.\n Ignoring new value."
                    
        th.parameterNames = ",".join(th.parameterNameList)
        #th.initialParameterValues = tuple(th.initialParameterValues)
        #
        # Update list of parameter names and values for all attached models
        #
        for currentModel in self.Models.values():
            currentModel.theory.parameterNames=th.parameterNames
            currentModel.theory.parameterNames0=th.parameterNames
            currentModel.theory.parameterNameList=th.parameterNameList
            currentModel.theory.parameterNameList0=th.parameterNameList
            currentModel.theory.initialParameterValues=tuple(th.initialParameterValues)
            currentModel.theory.initialParameterValues0=tuple(th.initialParameterValues)
        #
        # Remember original Names and values
        th.initialParameterValues0 = copy.copy(th.initialParameterValues)
        th.parameterNames0 = copy.copy(th.parameterNames)
        th.parameterNameList0 = copy.copy(th.parameterNameList)
        
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
        Sets parameters in fixedParamNames to their initial values,
        and updates the parameter values, names of the composite model
        heldParameters is a list of tuple(s) of the type: [('par1', val1)]
        """
        th = self.theory
        if heldParameters:
            pNames, pValues = self.reduceParameters(th.parameterNames0,\
                                                 th.initialParameterValues0,\
                                                 heldParameters)
            th.parameterNames = pNames
            th.parameterNameList = pNames.split(",")
            th.initialParameterValues = pValues
            for currentModel in self.Models.values():
                currentModel.theory.heldParameterBool = True
                currentModel.theory.HoldFixedParams(heldParameters)
            self.heldParamsPass = True
        else:
            if self.heldParamsPass:
                th.parameterNames = th.parameterNames0
                th.parameterNameList = th.parameterNameList0
                th.initialParameterValues = th.initialParameterValues0
                for currentModel in self.Models.values():
                    currentModel.theory.parameterNames=th.parameterNames0
                    currentModel.theory.parameterNameList=th.parameterNameList0
                    currentModel.theory.initialParameterValues=th.initialParameterValues0
                    currentModel.theory.heldParameterBool = False
                    currentModel.theory.heldParameterList = None
            
    def Residual(self, parameterValues):
        residuals = scipy.array([])
        for model in self.Models.values():
            modelResidual = model.Residual(parameterValues)
            residuals = scipy.concatenate((residuals,modelResidual))
        return residuals
        
    def Cost(self, parameterValues=None):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        residuals = self.Residual(parameterValues)
        return sum(residuals*residuals)
        #return sum(scipy.absolute(residuals))
    
    def SST(self, parameterValues=None):
        sst = 0.
        for model in self.Models.values():
            sst += model.SST(parameterValues)        
        return sst
        
    def R_square(self,parameterValues):
        """
        Calculates the R-square = 1 - cost / SST
        where SST is the sum of the squares about the mean
        """
        sst = self.SST(parameterValues)
        cost = self.Cost(parameterValues)
        return 1.- cost/sst
        
    def PlotFits(self, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.), figNumStart=1):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        figNum = figNumStart-1
        for model in self.Models.values():
            figNum+=1
            pylab.figure(figNum)
            model.PlotFits(parameterValues, fontSizeLabels, pylabLegendLoc)
            # Weird bug: repeating figure needed to get to show
            pylab.figure(figNum)
            
    def PlotCollapse(self, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.), figNumStart=1):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        figNum = figNumStart-1
        for model in self.Models.values():
            figNum+=1
            pylab.figure(figNum)
            model.PlotFunctions(parameterValues, fontSizeLabels, \
                                pylabLegendLoc, plotCollapse = True)
            pylab.figure(figNum)
            
    def BestFit(self,initialParameterValues=None):
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues
        out = scipy.optimize.minpack.leastsq(self.Residual, \
                initialParameterValues, full_output=1, ftol = 1e-16) 
        return out
        
    def PlotBestFit(self, initialParameterValues=None, \
                    figNumStart = 1, heldParams = None):
        
        if heldParams:
            if not isinstance(heldParams, list):
                heldParams = [helddParams]
            # Check now if the name is correct
            l_index = []
            for index, par in enumerate(heldParams):
                pName, pValue = par
                if pName not in self.theory.parameterNameList0:
                    print "%s is not a valid name. Ignored" % pName
                    l_index.append(index)
            if l_index:
                for i in l_index:
                    heldParams.pop(i)
                    
        # Call HoldFixedParams even if heldParams = None to check
        # if original Names and values have to be used
        self.HoldFixedParams(heldParams)
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues

        print 'initial cost = ', self.Cost(initialParameterValues)
        out = self.BestFit(initialParameterValues)
        optimizedParameterValues = out[0]
        covar = out[1]
        errors = [covar[i,i]**0.5 for i in range(len(covar))]
        #inv_t_student = scipy.special.stdtrit(len(errors),0.90)
        #errors = inv_t_student*errors
        print 'optimized cost = ', self.Cost(optimizedParameterValues)
        print 'optimized SST = ', self.SST(optimizedParameterValues)
        print 'R-value = ', self.R_square(optimizedParameterValues)
        print
        if heldParams:
            print "=== Held parameters ================"
            for pName,pValue in heldParams:
                print "%s = %2.2f" % (pName, pValue)
        # Print parameter values
        # YJC: changed printing here to print one sigma error instead of 95% confidence level
        print "=== Fitting parameters (with one sigma error)=============="
        for name, val, error in \
                zip(self.theory.parameterNameList,optimizedParameterValues, errors):
            print "%7s = %2.3f +/- %2.3f" %(name, val, error)
        print "====================================="
        #
        # Print plots
        #
        figNum = figNumStart-1
        for model in self.Models.values():
            for FT in [False,True]:
                figNum+=1
                pylab.figure(figNum)
                model.PlotFunctions(optimizedParameterValues, plotCollapse = FT)
                # Weird bug: repeating figure needed to get to show
                pylab.figure(figNum)
            figNum+=1
            pylab.figure(figNum)
            model.PlotResiduals(optimizedParameterValues)
            pylab.figure(figNum)
        #return optimizedParameterValues
        return out
