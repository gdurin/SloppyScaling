from __future__ import division
import matplotlib.pyplot as plt
import copy
import numpy as np
import scipy as sp
from scipy import exp, log
import scipy.optimize
import scipy.special


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
        self.totalSum = {}
        
    def installCurve(self, independent, fileName, defaultFractionalError = 0.3,\
                     pointSymbol="o", pointColor="b", \
                     xCol=0, yCol=1, errorCol=2, initialSkipIndex=0, initialSkipValue=None, factorError=1.0):
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
        self.initialSkip[independent] = 0
        self.pointType[independent] = pointColor + pointSymbol
        self.defaultFractionalError[independent] = defaultFractionalError
        try:
            infile = open(fileName, 'r')
            dataArray = sp.loadtxt(infile)
            infile.close()
            success = 1
            if initialSkipValue:
                x = dataArray[:,xCol]
                initialSkip = (x>=initialSkipValue).argmax()
            else:
                initialSkip = initialSkipIndex
            self.X[independent] = dataArray[initialSkip:,xCol]
            self.Y[independent] = dataArray[initialSkip:,yCol]
            cols = dataArray.shape[1]
            if errorCol >= 2 and cols > 2:
                self.errorBar[independent] =  dataArray[initialSkip:,errorCol] * factorError
            else:
                print "Errors not found"
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
    the cost, and the jacobian.
    """
    def __init__(self, theory, data, name, sorting):
        self.theory = theory
        self.data = data
        self.name = name
        self.sorting = sorting
        
    def dataTotalNumber(self):
        """
        returns the total number of the data to be fitted
        """
        n = 0
        for independentValues in self.data.experiments:
            initialSkip = self.data.initialSkip[independentValues]
            n+= len(self.data.X[independentValues][initialSkip:])
        return n

    def jacobian(self, parameterValues):
        for i, independentValues in enumerate(self.data.experiments):
            initialSkip = self.data.initialSkip[independentValues]
            X = self.data.X[independentValues][initialSkip:]
            Y = self.data.Y[independentValues][initialSkip:]
            errorBar = self.data.errorBar[independentValues][initialSkip:]
            thJacobian = self.theory.jacobian(X, Y, parameterValues, independentValues)/errorBar
            if i == 0:
                J = thJacobian
            else:
                J = sp.concatenate((J,thJacobian),1)
        return J
        
        
    def residual(self, parameterValues, dictResiduals=False):
        """
        Calculate the weighted residuals,
        with the weights = 1 / errorbar
        """
        if dictResiduals:
            residuals = {}
        else:
            residuals = sp.array([])
            
        for independentValues in self.data.experiments:
            initialSkip = self.data.initialSkip[independentValues]
            X = self.data.X[independentValues][initialSkip:]
            Y = self.data.Y[independentValues][initialSkip:]
            errorBar = self.data.errorBar[independentValues][initialSkip:]
            Ytheory = self.theory.Y(X, parameterValues, independentValues)
            res = (Ytheory-Y)/errorBar
            #res = (scipy.log10(Ytheory)-scipy.log10(Y))/errorBar
            if dictResiduals:
                residuals[independentValues] = res
            else:
                residuals = sp.concatenate((residuals,res))
        return residuals
        
    
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
            sst_partial = (Y-sp.mean(Y))/errorBar
            sst += sum(sst_partial*sst_partial)
        return sst
    
    def R_square(self,parameterValues=None):
        """
        Calculates the R-square = 1 - cost / SST
        where SST is the sum of the squares about the mean
        """
        sst = self.SST(parameterValues)
        cost = self.cost(parameterValues)
        return 1.- cost/sst
        

    
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
            log_i = sp.log10(i)
            d, I = sp.modf(log_i)
            if log_i < 0:
                add = 0.5 *(sp.absolute(d)<0.5)
            else:
                add = 0.5 *(sp.absolute(d)>0.5)
            m = sp.floor(log_i) + add
            out.append(10**m)
            log_j = sp.log10(j)
            d, I = sp.modf(log_j)
            if log_j < 0:
                add = - 0.5 *(sp.absolute(d)>0.5)
            else:
                add = - 0.5 *(sp.absolute(d)<0.5)
            m = sp.ceil(log_j) + add
            out.append(10**m)
        return tuple(out)
        
    def plotFunctions(self, parameterValues=None, plotCollapse = False, 
                fontSizeLabels = 18, fontSizeLegend=12, pylabLegendLoc=(0.,0.)):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        # XXX Having problems with plt.ioff()
        plt.ioff()
        plt.clf()
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
        
        #plt.plot([],label=r'$win (k/L)^{\sigma_k \zeta}$')
        
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
            plt.rcParams.update({'legend.fontsize':fontSizeLabels})
            #####################
            if self.data.linlog == 'log' or self.data.linlog == 'lin':
                if self.data.linlog == 'log':
                    plot_fn = getattr(plt,'loglog')
                elif self.data.linlog == 'lin':
                    plot_fn = getattr(plt,'plot')
                # Plot first data with their error
                plot_fn(X,Y,pointType[1])
                plt.errorbar(X,Y, yerr=y_error, fmt=pointType,label=lb)
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
                
        plt.axis(tuple(ax0))
        #plt.legend(loc=pylabLegendLoc, col=2)
        plt.legend(loc=pylabLegendLoc)
        if plotCollapse:
            plt.xlabel(self.theory.XscaledLatex, fontsize=fontSizeLabels)
            plt.ylabel(self.theory.YscaledLatex, fontsize=fontSizeLabels)
            plt.title(self.theory.scalingTitle)
        else:
            plt.xlabel(self.theory.XLatex, fontsize=fontSizeLabels)
            plt.ylabel(self.theory.YLatex, fontsize=fontSizeLabels)
            plt.title(self.theory.title, fontsize=fontSizeLabels)
        # XXX Turn on if ioff used plt.ion()
        plt.ion()
        plt.show()
        
    def plotResiduals(self, parameterValues=None, \
                      fontSizeLabels = 18, pylabLegendLoc=(0.2,0.)):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        plt.ioff()
        plt.clf()
        residuals = self.residual(parameterValues, dictResiduals=True)
        x0 = 0
        for independentValues in sorted(residuals):
            res = residuals[independentValues]
            xStep = len(res)
            x = range(x0,x0+xStep)
            x0 += xStep
            pointType = self.data.pointType[independentValues]
            lb = self.getLabel(self.theory.independentNames, independentValues)
            plt.plot(x,res,pointType, label=lb)
        plt.ylabel("Weighted residuals")
        plt.axhline(y=0,color='k')
        plt.legend(loc=pylabLegendLoc)
        plt.ion()
        plt.show()
        
    def bestFit(self,initialParameterValues = None,isJacobian=True):
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues
        if isJacobian:
            jacobian = self.jacobian
            out = scipy.optimize.minpack.leastsq(self.residual, \
                initialParameterValues,Dfun=jacobian, \
                col_deriv=True, warning=True, full_output=1, ftol=1.e-16) 
        else:
            out = scipy.optimize.minpack.leastsq(self.residual, \
                initialParameterValues, full_output=1, ftol=1.e-16) 
        return out
    
    def plotBestFit(self, initialParameterValues = None, \
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

        self.theory.holdFixedParams(heldParams)
   
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues
        
        print 'initial cost = ', self.cost(initialParameterValues)
        optimizedParameterValues = self.bestFit(initialParameterValues)[0]
        covar = self.bestFit(initialParameterValues)[1]
        errors = [covar[i,i]**0.5 for i in range(len(covar))]
        print 'optimized cost = ', self.cost(optimizedParameterValues)
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
        plt.figure(figFit)
        self.plotFunctions(optimizedParameterValues)
        plt.figure(figCollapse)
        self.plotFunctions(optimizedParameterValues, plotCollapse = True)        
        #YJC: need to call these twice to show figures properly
        plt.figure(figFit)
        plt.figure(figCollapse)
        return optimizedParameterValues

class CompositeModel:
    """
    Class combining several Models into one
    The main job of CompositeModel is to combine the parameter lists and
    initial values into a single structure, and then to impose that structure
    on the individual theories.
    Also, plots and stuff should be delegated to the individual theories.
    """
    parameterNames = ""
    initialParameterValues = []
    parameterNameList = []
    
    #class CompositeTheory:
        #def __init__(self):
            #self.parameterNames = ""
            #self.initialParameterValues = []
            #self.parameterNameList = []
            
    def __init__(self, name):
        self.models = {}
        #self.theory = self.CompositeTheory()
        self.name = name
        self.heldParamsPass = False
        
    def installModel(self,modelName, model):
        self.models[modelName] = model
        #th = self.theory
        for param, init in zip(model.theory.parameterNameList, \
                                model.theory.initialParameterValues):
            if param not in CompositeModel.parameterNameList:
                CompositeModel.parameterNameList.append(param)
                CompositeModel.initialParameterValues.append(init)
            else:
                # Check if shared param has consistent initial value
                # between models
                paramCurrentIndex = CompositeModel.parameterNameList.index(param)
                paramCurrentInitialValue = \
                        CompositeModel.initialParameterValues[paramCurrentIndex]
                if paramCurrentInitialValue != init:
                    print "Initial value %f"%(init,) \
                     + " for parameter " + param + " in model " + modelName \
                     + " \n disagrees with value %f"%(paramCurrentInitialValue)\
                     + " already stored for previous theory in " \
                     + " CompositeTheory.\n Ignoring new value."
                    
        CompositeModel.parameterNames = ",".join(CompositeModel.parameterNameList)
        # CompositeModel.initialParameterValues = tuple(CompositeModel.initialParameterValues)
        #
        # Update list of parameter names and values for all attached models
        #
        for currentModel in self.models.values():
            currentModel.theory.parameterNames=CompositeModel.parameterNames
            currentModel.theory.parameterNames0=CompositeModel.parameterNames
            currentModel.theory.parameterNameList=CompositeModel.parameterNameList
            currentModel.theory.parameterNameList0=CompositeModel.parameterNameList
            currentModel.theory.initialParameterValues=tuple(CompositeModel.initialParameterValues)
            currentModel.theory.initialParameterValues0=tuple(CompositeModel.initialParameterValues)
        #
        # Remember original Names and values
        CompositeModel.initialParameterValues0 = copy.copy(CompositeModel.initialParameterValues)
        CompositeModel.parameterNames0 = copy.copy(CompositeModel.parameterNames)
        CompositeModel.parameterNameList0 = copy.copy(CompositeModel.parameterNameList)
        
    def reduceParameters(self,pNames,pValues,heldParams):
        list_params = pNames.split(",")
        list_initials = list(pValues)
        print list_params
        print heldParams
        for param_to_remove, val in heldParams:
            try:
                index = list_params.index(param_to_remove)
                list_params.pop(index)
                list_initials.pop(index)
            except ValueError:
                print "Warning: parameter ", param_to_remove, " NOT included in the list"
        return ",".join(list_params), tuple(list_initials)
        
    def holdFixedParams(self, heldParameters):
        """
        Sets parameters in fixedParamNames to their initial values,
        and updates the parameter values, names of the composite model
        heldParameters is a list of tuple(s) of the type: [('par1', val1)]
        """
        if heldParameters:
            CompositeModel.parameterNames, CompositeModel.initialParameterValues \
                          = self.reduceParameters(CompositeModel.parameterNames0,\
                            CompositeModel.initialParameterValues0, heldParameters)
            CompositeModel.parameterNameList = CompositeModel.parameterNames.split(",")
            for currentModel in self.models.values():
                currentModel.theory.heldParameterBool = True
                currentModel.theory.holdFixedParams(heldParameters)
            self.heldParamsPass = True
        else:
            if self.heldParamsPass:
                CompositeModel.parameterNames = CompositeModel.parameterNames0
                CompositeModel.parameterNameList = CompositeModel.parameterNameList0
                CompositeModel.initialParameterValues = CompositeModel.initialParameterValues0
                for currentModel in self.models.values():
                    currentModel.theory.parameterNames=CompositeModel.parameterNames0
                    currentModel.theory.parameterNameList=CompositeModel.parameterNameList0
                    currentModel.theory.initialParameterValues=CompositeModel.initialParameterValues0
                    currentModel.theory.heldParameterBool = False
                    currentModel.theory.heldParameterList = None
    
    def dataTotalNumber(self):
        n = 0
        for model in self.models.values():
            n+= model.dataTotalNumber()
        return n
                    
    def residual(self, parameterValues):
        residuals = sp.array([])
        for model in self.models.values():
            residuals = sp.concatenate((residuals,model.residual(parameterValues)))
        return residuals
        
    def cost(self, parameterValues=None):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        residuals = self.residual(parameterValues)
        cst = np.dot(residuals, residuals)
        dataTotalNumber = self.dataTotalNumber()
        dof = float(dataTotalNumber-len(parameterValues))
        # Standard error of the regression 
        # see parameter SER in 
        # http://en.wikipedia.org/wiki/Linear_least_squares
        ser = (cst/dof)**0.5
        return cst, ser
    
    def SST(self, parameterValues=None):
        sst = 0.
        for model in self.models.values():
            sst += model.SST(parameterValues)        
        return sst
        
    def R_square(self,parameterValues):
        """
        Calculates the R-square = 1 - cost / SST
        where SST is the sum of the squares about the mean
        """
        sst = self.SST(parameterValues)
        cost = self.cost(parameterValues)
        return 1.- cost/sst
        
    def plotFits(self, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.), figNumStart=1):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        figNum = figNumStart-1
        for model in self.models.values():
            figNum+=1
            plt.figure(figNum)
            model.plotFits(parameterValues, fontSizeLabels, pylabLegendLoc)
            # Weird bug: repeating figure needed to get to show
            plt.figure(figNum)
            
    def plotCollapse(self, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.), figNumStart=1):
        if parameterValues is None:
            parameterValues = self.theory.initialParameterValues
        figNum = figNumStart-1
        for model in self.models.values():
            figNum+=1
            plt.figure(figNum)
            model.plotFunctions(parameterValues, fontSizeLabels, \
                                pylabLegendLoc, plotCollapse = True)
            plt.figure(figNum)
            
    def jacobian(self, parameterValues):
        for i,model in enumerate(self.models.values()):
            if i == 0:
                J = model.jacobian(parameterValues)
            else:
                J = numpy.concatenate((J,model.jacobian(parameterValues)),1)
        return J
            
    def bestFit(self,initialParameterValues=None,isJacobian=False):
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues
        if isJacobian:
            out = scipy.optimize.minpack.leastsq(self.residual, \
                initialParameterValues, Dfun=self.jacobian, \
                col_deriv=True, warning=True, full_output=1, ftol=1.e-16)
        else:
            out = scipy.optimize.minpack.leastsq(self.residual, \
                initialParameterValues, full_output=1, ftol = 1e-16) 
        return out
        
    def plotBestFit(self, initialParameterValues=None, \
                    figNumStart = 1, heldParams = None):
        from time import time
        t0 = time()
        # Unicode characters
        uniSymbol = {'tau': unichr(964), 'sigma_k': unichr(963)+"_k",\
                         'zeta': unichr(950)}
        
        if heldParams:
            if not isinstance(heldParams, list):
                heldParams = [heldParams]
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
                    
        # Call holdFixedParams even if heldParams = None to check
        # if original Names and values have to be used
        self.holdFixedParams(heldParams)
        if initialParameterValues is None:
            initialParameterValues = self.theory.initialParameterValues

        print 'initial cost = ', self.cost(initialParameterValues)
        out = self.bestFit(initialParameterValues)
        
        print out[0]
        optimizedParameterValues = out[0]
        covar = out[1]
        errors = [covar[i,i]**0.5 for i in range(len(covar))]
        #errors = [1 for i in range(len(optimizedParameterValues))]        
        #inv_t_student = sp.special.stdtrit(len(errors),0.90)
        #errors = inv_t_student*errors
        print 'optimized cost = ', self.cost(optimizedParameterValues)
        #print 'optimized SST = ', self.SST(optimizedParameterValues)
        #print 'R-value = ', self.R_square(optimizedParameterValues)
        #print
        if heldParams:
            print "=== Held parameters ================"
            for pName,pValue in heldParams:
                if pName in uniSymbol:
                    print "%3s = %2.2f" % (uniSymbol[pName], pValue)
                else:
                    print "%3s = %2.2f" % (pName, pValue)
        # Print parameter values
        # YJC: changed printing here to print one sigma error instead of 95% confidence level
        print "=== Fitting parameters (with one sigma error)=============="
        for name, val, error in \
            zip(self.theory.parameterNameList,optimizedParameterValues, errors):
            if name in uniSymbol:
                print "%3s = %2.3f +/- %2.3f" %(uniSymbol[name], val, error)
            else:
                print "%3s = %2.3f +/- %2.3f" %(name, val, error)
        print "====================================="
        print "n. of function calls = ", out[2]['nfev']
        print out[3:]
        #
        # Print plots
        #
        figNum = figNumStart-1
        for model in self.models.values():
            for FT in [False,True]:
                figNum+=1
                plt.figure(figNum)
                model.plotFunctions(optimizedParameterValues, plotCollapse = FT)
                # Weird bug: repeating figure needed to get to show
                plt.figure(figNum)
            figNum+=1
            plt.figure(figNum)
            model.plotResiduals(optimizedParameterValues)
            plt.figure(figNum)
        #return optimizedParameterValues
        ts = round(time() - t0, 3)
        print "*** Time elapsed:", ts
        return out
