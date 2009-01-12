import scipy
import pylab
from scipy import exp
import scipy.optimize

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
    sizeHisto = ScalingTheory('S**(-tau) * exp((-(S*(R-Rc)**sigma)/XS)**nS)',
                'tau, sigma, XS, nS, Rc', (1.5,0.5,1.0,1.0,2.0),
                independentNames = 'R',
                scalingX = 'S*r**sigma', scalingY = 'D*S**tau',
                scalingXTeX = r'$S r^\sigma$',
                scalingYTeX = r'$D S^\tau$',
                title= 'Avalanche histo$'
                scalingTitle= 'Avalanche histo scaling plot'
                Xname = 'S', Yname = 'D', normalization = True)
    """
    def __init__(_, Ytheory, parameterNames, initialParameterValues, \
                 independentNames, \
                 scalingX = 'X', scalingY = 'Y', \
                 scalingXTeX = r'${\cal{X}}$', \
                 scalingYTeX = r'${\cal{Y}}$', \
                 title = 'Fit', scalingTitle = 'Scaling Collapse',
                 Xname='X', Yname='Y', normalize = False):
        _.Ytheory = Ytheory
        _.parameterNames = parameterNames
        _.parameterNameList = parameterNames.split(",")
        _.initialParameterValues = initialParameterValues
        _.independentNames = independentNames
        _.Xname = Xname
        _.Yname = Yname
        _.scalingX = scalingX
        _.scalingY = scalingY
        _.scalingXTeX = scalingXTeX
        _.scalingYTeX = scalingYTeX
        _.title = title
        _.scalingTitle = scalingTitle
        _.scalingY = scalingY
        _.normalize = normalize
    def Y(_, X, parameterValues, independentValues):
        """
        Predicts Y as a function of X
        """
        # Set values of parameters based on vector of current guess
        # Set values of independent variables based on which curve is being fit
        # Set up vector of independent variable from X
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        exec(_.parameterNames + " = parameterValues")
        exec(_.independentNames + " = independentValues")
        exec(_.Xname + ' = X')
        exec("Y = " + _.Ytheory)
        if _.normalize:
            Y = _.Norm(X, Y, parameterValues, independentValues)
        return Y
    def ScaleX(_, X, parameterValues, independentValues):
        """
        Rescales X according to scaling form
        """
        # Set values of parameters, independent variables, and X vector
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        exec(_.parameterNames + " = parameterValues")
        exec(_.independentNames + " = independentValues")
        exec(_.Xname + ' = X')
        exec("XScale = " + _.scalingX)
        return XScale
    def ScaleY(_, X, Y, parameterValues, independentValues):
        """
        Rescales Y according to scaling form
        """
        # Set values of parameters, independent variables, and X vector
        # Warning: local variables in subroutine must be named
        # 'parameterValues', 'independentValues', and 'X'
        exec(_.parameterNames + " = parameterValues")
        exec(_.independentNames + " = independentValues")
        exec(_.Xname + ' = X')
        exec(_.Yname + "= Y")
        exec("YScale = " + _.scalingY)
        return YScale
    #
    # Various options for normalization
    #
    def NormBasic(_, X, Y, parameterValues, independentValues):
        """
        Must guess at bin sizes for first and last bins
        """
        norm = Y[0]*(X[1]-X[0])
        norm += sum(Y[1:-1] * (X[2:]-X[:-2])/2.0)
        norm += Y[-1]*(X[-1]-X[-2])
        return Y/norm
    def NormIntegerSum(_, X, Y, parameterValues, independentValues, \
                xStart=1., xEnd=1024.):
        """
        Function summed over positive integers equals one; brute force
        up to xEnd
        """
        x = scipy.arange(xStart, xEnd)
        return Y/sum(_.Y(x, parameterValues, independentValues))
    Norm = NormBasic # Overload if desired

class Data:
    """
    A Data object contains a series of curves each for a set of independent
    control parameters. For example, the X values might be avalanche sizes
    (Xname = 'S'), the Y values might be percentage area covered by
    avalalanches of that size (Yname = 'A'),
    the sigmas the standard errors in the means, and an independent control
    parameters might be the demagnetizing field (independent = 'k'). If,
    as for A(S), the data plots are typically log-log set _.linlog = 'log';
    for things like V(t,T) set _.linlog = 'lin'.
    """ 
    def __init__(_, linlog = 'log'):
        _.experiments = []
        _.X = {}
        _.Y = {}
        _.linlog = linlog
        _.pointType = {}
        _.errorBar = {}
        _.fileNames = {}
        _.defaultFractionalError = {}
        _.initialSkip = {}
    def InstallCurve(_, independent, fileName, defaultFractionalError = 0.1,\
                     pointSymbol="o", pointColor="b", \
                     xCol=0, yCol=1, errorCol = 2, initialSkip = 0):
        """
        Curves for independent control parameters given by "independent"
        loaded from "fileName". Plots use, for example, pointSymbol from 
            ['o','^','v','<','>','s', 'p', 'h','+','x']
        and pointColor from 
            ['b','g','r','c','m','burlywood','chartreuse']
        """
        independent = tuple(independent)
        _.experiments.append(independent)
        _.fileNames[independent] = fileName
        _.initialSkip[independent] = initialSkip
        _.pointType[independent] = pointColor + pointSymbol
        _.defaultFractionalError[independent] = defaultFractionalError
        try:
            infile = open(fileName, 'r')
            lines = infile.readlines()
            infile.close()
            numbers = [line.split() for line in lines]
            _.X[independent] = scipy.array( \
                        [float(line[xCol]) for line in numbers])
            _.Y[independent] = scipy.array( \
                        [float(line[yCol]) for line in numbers])
            if errorCol is not None:
                _.errorBar[independent] =  \
                        scipy.array([float(line[errorCol]) for line in numbers])
            else:
                _.errorBar[independent] = \
                    _.Y[independent] * defaultFractionalError
        except IOError:
            print "File %s not found"%fileName

class Model:
    """
    A Model object unites Theory with Data. It's primary task is to 
    calculate the residuals (the difference between theory and data)
    and the cost.
    """
    def __init__(_, theory, data, name):
        _.theory = theory
        _.data = data
        _.name = name
    def Residual(_, parameterValues):
        residuals = []
        for independentValues in _.data.experiments:
            initialSkip = _.data.initialSkip[independentValues]
            X = _.data.X[independentValues][initialSkip:]
            Y = _.data.Y[independentValues][initialSkip:]
            errorBar = _.data.errorBar[independentValues][initialSkip:]
            Ytheory = _.theory.Y(X, parameterValues, independentValues)
            # XXX Likely a better way to merge scipy arrays into big one
            residuals = residuals + list((Ytheory-Y)/errorBar)
        return scipy.array(residuals)
    def Cost(_, parameterValues=None):
        if parameterValues is None:
            parameterValues = _.theory.initialParameterValues
        residuals = _.Residual(parameterValues)
        return sum(residuals*residuals)
    def PlotFits(_, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.)):
        if parameterValues is None:
            parameterValues = _.theory.initialParameterValues
        # XXX Having problems with pylab.ioff()
        pylab.ioff()
        # Bug in pylab:
        # can't do "legend", "errorbar", and "clf" on the same plot
        pylab.clf()
        if _.data.linlog == 'log':
            minY = 1.e99
            for independentValues in _.data.experiments:
                minY = min(minY, min(_.data.Y[independentValues]))
        for independentValues in _.data.experiments:
            X = _.data.X[independentValues]
            Y = _.data.Y[independentValues]
            pointType = _.data.pointType[independentValues]
            errorBar = _.data.errorBar[independentValues]
            # Avoid error bars crossing zero on log-log plots:
            if _.data.linlog == 'log':
                errorBarDown = errorBar * (errorBar < Y) \
                                + (Y-minY) * (errorBar > Y)
            Ytheory = _.theory.Y(X, parameterValues, independentValues)
            lb = _.theory.independentNames + "=" + str(independentValues)
            lb = _.theory.independentNames + "="
            lb += str(independentValues[0])
            for val in independentValues[1:]:
                lb += "," + str(val)
            if _.data.linlog == 'log':
                pylab.errorbar(X,Y,fmt=pointType,yerr=[errorBarDown,errorBar],\
                                label=lb)
                pylab.loglog(X,Ytheory,pointType[0])
            elif _.data.linlog == 'lin':
                pylab.errorbar(X,Y,fmt=pointType, yerr=errorBar,label=lb)
                pylab.plot(X,Ytheory,pointType[0])
            else:
                 print "Format " + _.data.linlog + \
                        " not supported yet in PlotFits"
        pylab.xlabel(_.theory.Xname, fontsize = fontSizeLabels)
        pylab.ylabel(_.theory.Yname, fontsize = fontSizeLabels)
        pylab.legend(loc=pylabLegendLoc)
        pylab.title(_.theory.title)
        # XXX Turn on if ioff used pylab.ion()
        pylab.ion()
        pylab.show()
    def PlotCollapse(_, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.)):
        if parameterValues is None:
            parameterValues = _.theory.initialParameterValues
        # XXX Having problems with pylab.ioff()
        pylab.ioff()
        # Bug in pylab:
        # can't do "legend", "errorbar", and "clf" on the same plot
        pylab.clf()
        if _.data.linlog == 'log':
            minYscaled = 1.e99
            for independentValues in _.data.experiments:
                X = _.data.X[independentValues]
                Y = _.data.Y[independentValues]
                Yscaled = _.theory.ScaleY(X,Y,parameterValues,independentValues)
                minYscaled = min(minYscaled,min(Yscaled))
        for independentValues in _.data.experiments:
            X = _.data.X[independentValues]
            Xscaled = _.theory.ScaleX(X, parameterValues, independentValues)
            Y = _.data.Y[independentValues]
            Yscaled = _.theory.ScaleY(X, Y, parameterValues, independentValues)
            pointType = _.data.pointType[independentValues]
            errorBar = _.data.errorBar[independentValues]
            errorBarScaled = _.theory.ScaleY(X, errorBar, \
                                parameterValues, independentValues)
            # Avoid error bars crossing zero on log-log plots
            if _.data.linlog == 'log':
                errorBarDownScaled = \
                        errorBarScaled * (errorBarScaled < Yscaled) \
                     + (Yscaled-minYscaled) * (errorBarScaled > Yscaled)
            Ytheory = _.theory.Y(X, parameterValues, independentValues)
            YtheoryScaled = _.theory.ScaleY(X, Ytheory, parameterValues, \
                                independentValues)
            lb = _.theory.independentNames + "=" + str(independentValues)
            lb = _.theory.independentNames + "="
            lb += str(independentValues[0])
            for val in independentValues[1:]:
                lb += "," + str(val)
            if _.data.linlog == 'log':
                pylab.errorbar(Xscaled,Yscaled, \
                                yerr=[errorBarDownScaled,errorBarScaled], \
                                fmt=pointType,label=lb)
                pylab.loglog(Xscaled,YtheoryScaled,pointType[0])
            elif _.data.linlog == 'lin':
                pylab.errorbar(Xscaled,Yscaled,yerr=errorBarScaled, \
                                fmt=pointType,label=lb)
                pylab.plot(X,Ytheory,pointType[0])
            else:
                 print "Format " + _.data.linlog + \
                        " not supported yet in PlotFits"
        pylab.xlabel(_.theory.scalingXTeX, fontsize = fontSizeLabels)
        pylab.ylabel(_.theory.scalingYTeX, fontsize = fontSizeLabels)
        pylab.legend(loc=pylabLegendLoc)
        pylab.title(_.theory.scalingTitle)
        # XXX Turn on if ioff used pylab.ion()
        pylab.ion()
        pylab.show()
    def BestFit(_,initialParameterValues = None):
        if initialParameterValues is None:
            initialParameterValues = _.theory.initialParameterValues
        out = scipy.optimize.minpack.leastsq(_.Residual, \
                initialParameterValues, full_output=1) 
        return out[0]
    def PlotBestFit(_, initialParameterValues = None, \
                    figFit = 1, figCollapse=2):
        if initialParameterValues is None:
            initialParameterValues = _.theory.initialParameterValues
        print 'initial cost = ', _.Cost(initialParameterValues)
        optimizedParameterValues = _.BestFit(initialParameterValues)
        print 'optimized cost = ', _.Cost(optimizedParameterValues)
        for name, val in \
                zip(_.theory.parameterNameList,optimizedParameterValues):
            print name + " = ", val
        pylab.figure(figFit)
        _.PlotFits(optimizedParameterValues)
        pylab.figure(figCollapse)
        _.PlotCollapse(optimizedParameterValues)
        # XXX JPS: Why do I need to do this to raise figures?
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
        def __init__(_):
            _.parameterNames = ""
            _.initialParameterValues = []
            _.parameterNameList = []
    def __init__(_, name):
        _.Models = {}
        _.theory = _.CompositeTheory()
        _.name = name
    def InstallModel(_,modelName, model):
        _.Models[modelName] = model
        th = _.theory
        for param, init in zip(model.theory.parameterNameList, \
                                model.theory.initialParameterValues):
            if param not in th.parameterNameList:
                th.parameterNameList.append(param)
                if len(th.parameterNames) == 0:
                    th.parameterNames += param
                else:
                    th.parameterNames += "," + param
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
        #
        # Update list of parameter names and values for all attached models
        #
        for currentModel in _.Models.values():
            currentModel.theory.parameterNames=th.parameterNames
            currentModel.theory.parameterNameList=th.parameterNameList
            currentModel.theory.initialParameterValues=th.initialParameterValues
    def Residual(_, parameterValues):
        residuals = []
        for model in _.Models.values():
            modelResidual = model.Residual(parameterValues)
            residuals = residuals + list(modelResidual)
        return scipy.array(residuals)
    def Cost(_, parameterValues=None):
        if parameterValues is None:
            parameterValues = _.theory.initialParameterValues
        residuals = _.Residual(parameterValues)
        return sum(residuals*residuals)
    def PlotFits(_, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.), figNumStart=1):
        if parameterValues is None:
            parameterValues = _.theory.initialParameterValues
        figNum = figNumStart-1
        for model in _.Models.values():
            figNum+=1
            pylab.figure(figNum)
            model.PlotFits(parameterValues, fontSizeLabels, pylabLegendLoc)
            # Weird bug: repeating figure needed to get to show
            pylab.figure(figNum)
    def PlotCollapse(_, parameterValues=None, \
                 fontSizeLabels = 18, pylabLegendLoc=(0.2,0.), figNumStart=1):
        if parameterValues is None:
            parameterValues = _.theory.initialParameterValues
        figNum = figNumStart-1
        for model in _.Models.values():
            figNum+=1
            pylab.figure(figNum)
            model.PlotCollapse(parameterValues, fontSizeLabels, pylabLegendLoc)
            pylab.figure(figNum)
    def BestFit(_,initialParameterValues = None):
        if initialParameterValues is None:
            initialParameterValues = _.theory.initialParameterValues
        out = scipy.optimize.minpack.leastsq(_.Residual, \
                initialParameterValues, full_output=1) 
        return out[0]
    def PlotBestFit(_, initialParameterValues = None, \
                    figNumStart = 1):
        if initialParameterValues is None:
            initialParameterValues = _.theory.initialParameterValues
        print 'initial cost = ', _.Cost(initialParameterValues)
        optimizedParameterValues = _.BestFit(initialParameterValues)
        print 'optimized cost = ', _.Cost(optimizedParameterValues)
        # Print parameter values
        for name, val in \
                zip(_.theory.parameterNameList,optimizedParameterValues):
            print name + " = ", val
        figNum = figNumStart-1
        for model in _.Models.values():
            figNum+=1
            pylab.figure(figNum)
            model.PlotFits(optimizedParameterValues)
            # Weird bug: repeating figure needed to get to show
            pylab.figure(figNum)
            figNum+=1
            pylab.figure(figNum)
            model.PlotCollapse(optimizedParameterValues)
            pylab.figure(figNum)
        return optimizedParameterValues
