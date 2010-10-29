import os, platform, sys, glob
import numpy as np
from time import time
from PyQt4 import QtCore 
from PyQt4 import QtGui
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg \
     import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
     import NavigationToolbar2QTAgg as NavigationToolbar
import editfunctiondlg
import ui_main
#import helpform
import qrc_resources
from sloppyscaling import CompositeModel
from setupmodule import Module
from getFunctions import getFunctionNames
import getData


__version__ = "0.1.0"

FONTSIZELABELS = 15
FONTSIZEAXIS = 18
mpl.rcParams.update({'legend.fontsize':FONTSIZELABELS})
#sys.setrecursionlimit(1500)

myDir = "/home/gf/meas/Simulation/LIM"


dirs = 'images','files', 'functions'
dirImages, dirFiles, dirFunctions = dirs
for d in dirs:
    if not os.path.isdir(d):
        os.path.os.mkdir(d)

def getAxis(axis):
    """
    This function enlarges the axis limits up/down 
    to the closest 10**integer value
    """
    ax0 = []
    for i, ax in enumerate(axis):
        exponent = np.floor(np.log10(ax))
        int_rational = int(ax/10**exponent)
        ax0.append(i%2 and (int_rational+2)*10**exponent \
                   or (int_rational)*10**exponent)
    return tuple(ax0)

class SelectFunction(QtGui.QDialog):
    """
    Dialog to select an existing function
    """
    def __init__(self, msg="Select a function", parent=None):
        super(SelectFunction, self).__init__(parent)
        self.functionNames = sorted(getFunctionNames())
        if self.functionNames:
            self.box = QtGui.QDialogButtonBox()
            for function in self.functionNames:
                self.box.addButton(function, QtGui.QDialogButtonBox.AcceptRole)
            self.box.setOrientation(QtCore.Qt.Vertical)
            self.box.setCenterButtons(True)
            self.box.adjustSize()
            for button in self.box.buttons():
                self.connect(button, QtCore.SIGNAL("clicked()"), self.buttonClicked)
            title = QtGui.QLabel()
            title.setText(msg)
            buttonsLayout = QtGui.QHBoxLayout()
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(self.box)
            buttonsLayout.addStretch()
            vertLayout = QtGui.QVBoxLayout()
            vertLayout.setAlignment
            vertLayout.addWidget(title)
            vertLayout.addLayout(buttonsLayout)
            self.setLayout(vertLayout)
            self.setWindowTitle(msg)
        else:
            print "error"
    
    def buttonClicked(self):
        button = self.sender()
        #index = self.box.buttons().index(button)        
        #self.choice = self.functionNames[index]
        self.choice = str(button.text())
        self.accept()
    
class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, \
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MainWindow(QtGui.QMainWindow,ui_main.Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #self.dirty = False
        self.filename = None
        self.printer = None
        self.parameterNames = {}
        self.isDataLoad = False
        self.isRunFitting = False
        self.setupUi(self)
        self.linlog = 'log' # To be set properly
        
        self.sizeLabel = QtGui.QLabel()
        self.sizeLabel.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.statusbar.addPermanentWidget(self.sizeLabel)
        self.statusbar.showMessage("Ready", 5000)
        # ShortCuts
        self.fileNewAction.setShortcut(QtGui.QKeySequence.New)
        self.fileOpenAction.setShortcut(QtGui.QKeySequence.Open)
        self.fileSaveAction.setShortcut(QtGui.QKeySequence.Save)
        self.fileSaveAsAction.setShortcut(QtGui.QKeySequence.SaveAs)
        self.fileQuitAction.setShortcut(QtGui.QKeySequence.Quit)
        self.connect(self.fileQuitAction,QtCore.SIGNAL("triggered()"), self.close)
        self.dataLoadAction.setShortcut("Ctrl+L")
        self.functionNewAction.setShortcut("Alt+N")
        

    def okToContinue(self, msgTitle="",msg=""):
        self.dirty = True
        if self.dirty:
            reply = QtGui.QMessageBox.warning(self,
                            msgTitle, msg, \
                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return False
            elif reply == QtGui.QMessageBox.Yes:
                return True
        return True


    ###################
    #### Triggered slots   #
    ###################
    @QtCore.pyqtSignature("")        
    def on_fileNewAction_triggered(self):
        if not self.okToContinue:
            return
        print "this is fileNewAction"

    @QtCore.pyqtSignature("")      
    def on_fileOpenAction_triggered(self):
        pass

    @QtCore.pyqtSignature("")  
    def on_fileSaveAction_triggered(self):
        pass

    @QtCore.pyqtSignature("")  
    def on_fileSaveAsAction_triggered(self):
        pass

    def closeEvent(self, event):
        print "ok this is the event", event 

    @QtCore.pyqtSignature("")  
    def on_dataLoadAction_triggered(self):
        """
        it loads Data from disk and associates them to function(s);
        it setups the corresponding module and plots them
        """
        # 0. Reset any information about previous plots
        self.dataPoints = {}
        self.functionLines = {}
        self.errorBars = {}
        # Setup the lists of canvas and the navtoolbars if not previous done 
        if not self.isDataLoad:
            self.figureCanvas = []
            self.navToolBar = []        
        # 
        # 1. Open the dialog with the DataSet table and the function choice
        #
        getFileNamesDlg = getData.InputDialog(myDir)
        if getFileNamesDlg.exec_():
            independentValues = getFileNamesDlg.independentValues
            self.moduleNames = getFileNamesDlg.moduleNames
            print "Done"
            #self.moduleNames = ['PDistr']
        # 2. replace the jointModule 
        # get the functions+data Names to install: 
        # these are called moduleNames
        jointModuleName = "".join(self.moduleNames)
        self.compositeModule = CompositeModel(jointModuleName)
        for i, moduleName in enumerate(self.moduleNames):
            # Install first the module and get the reference to the moduleObject
            model = Module(moduleName, independentValues)
            modelObject = model.modelObject
            self.statusbar.showMessage(model.loadedMsg)
            # Then add it to the compositeModule
            self.compositeModule.installModel(moduleName, modelObject)
            # get the final list of the parameter names
            self.independentNames = model.independentNames
        #
        # 3. Plot the raw data
        # Make a loop over the modules, i.e. the fitting function
        # and open a new tab if needed
        # Get all the models in a sorted list
        self.modelKeys = sorted(self.compositeModule.models)
        for i, key in enumerate(self.modelKeys):
            # First prepare the tab in the widget
            if not self.isDataLoad:
                setTab = "tab_%s" % i
                # The first tab "ta_0" is already set by Qt Designer (should I drop this)?
                if hasattr(self, setTab):
                    tab = getattr(self, setTab)
                    self.tabWidget.setTabText(0, self.moduleNames[i])
                else:
                    exec "self.%s = QtGui.QWidget()" % setTab
                    exec "tab  = self.%s" % setTab
                    tab.setObjectName(setTab)
                    index = self.tabWidget.addTab(tab, "")
                    self.tabWidget.setTabText(index, self.moduleNames[i])
                plotVBox = QtGui.QVBoxLayout(tab)
                figureCanvas = MplCanvas(tab)
                self.figureCanvas.append(figureCanvas)
                navToolBar = NavigationToolbar(figureCanvas, tab)
                self.navToolBar.append(navToolBar)
                plotVBox.addWidget(figureCanvas)
                plotVBox.addWidget(navToolBar)            
            # Then plot the data
            model = self.compositeModule.models[key]
            self.plotRawData(self.figureCanvas[i], model.data)
        self.statusbar.showMessage("Data loaded", 5000)
        self.isDataLoad = True
                
    def plotRawData(self, figureCanvas, data):
        """
        plot Data (X, Y, errorBar) in a Canvas
        """
        figureCanvas.axes.cla() # Clean the canvas everytime it is called
        for independentValues in data.experiments:
            X,Y = data.X[independentValues], data.Y[independentValues]
            pointType = data.pointType[independentValues]
            exp_data, = figureCanvas.axes.loglog(X, Y)
            exp_data.set_color(pointType[0])
            marker, line = pointType[1], 'None'
            exp_data.set_marker(marker)
            exp_data.set_linestyle(line)
            # Set the errorbars
            errorBar = data.errorBar[independentValues]
            # Avoid error bars crossing zero on log-log plots
            if self.linlog == 'log':
                errorBarDown = errorBar * (errorBar < Y) + (Y -min(Y)) * (errorBar > Y)
                y_error=[errorBarDown,errorBar]
            else:
                y_error=errorBar
            figureCanvas.axes.errorbar(X,Y, yerr=y_error, fmt=pointType)
        figureCanvas.axes.autoscale(True, tight=True)
        self.XYlimits = figureCanvas.axes.axis()
        figureCanvas.axes.axis(getAxis(self.XYlimits))
        figureCanvas.draw()
        
    def linlogSpace(self, X, ntimes=10):
        """
        add more points to the X (useful for functions)
        """
        minX, maxX = min(X), max(X)
        if self.linlog == 'lin':
            X = np.linspace(minX, maxX, len(X)*ntimes)
        else:
            X = np.logspace(np.log10(minX), np.log10(maxX), len(X)*ntimes)
        return X
    
    def getLabel(self, names, values, withRescale = False):
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
        
    def plotDataAndFunction(self, figureCanvas, data, theory, parameterValues, plotCollapse=None):
        """
        function to plot the fitting Funtion in a Canvas
        """
        rangeX = 0.
        for independentValues in data.experiments:
            X = data.X[independentValues]
            Y = data.Y[independentValues]
            Ytheory = theory.Y(X, parameterValues, independentValues)
            pointType = data.pointType[independentValues]
            errorBar = data.errorBar[independentValues]
            if plotCollapse:
                # Scaled error bars and Y need not-rescaled X
                errorBar = theory.ScaleY(X, errorBar, parameterValues, \
                                              independentValues)
                Y = theory.ScaleY(X, Y, parameterValues, independentValues)
                if self.linlog == 'log':
                    Xtheory = np.logspace(np.log10(min(X)), np.log10(max(X)), 50)
                else:
                    Xtheory = np.linspace(min(X), max(X), 50)
                Ytheory = theory.Y(Xtheory, parameterValues, independentValues)
                Ytheory = theory.ScaleY(Xtheory, Ytheory, parameterValues, independentValues)
                Xtheory = theory.ScaleX(Xtheory, parameterValues, independentValues)
                # Then rescale X too
                X = theory.ScaleX(X, parameterValues, independentValues)
            else:
                X = self.linlogSpace(X)
                Ytheory = theory.Y(X, parameterValues, independentValues)
            # Avoid error bars crossing zero on log-log plots
            if self.linlog == 'log':
                errorBarDown = errorBar * (errorBar < Y) + (Y -min(Y)) * (errorBar > Y)
                y_error=[errorBarDown,errorBar]
            else:
                y_error=errorBar
            # Prepare the labels
            lb = self.getLabel(theory.independentNames, independentValues)
            if plotCollapse:
                if not self.isRunFitting:
                    data_points, = figureCanvas.axes.loglog(X, Y, label=lb)
                    data_points.set_color(pointType[0])
                    marker, line = pointType[1], 'None'
                    data_points.set_marker(marker)
                    data_points.set_linestyle(line)
                    self.dataPoints[figureCanvas, independentValues] = data_points
                    self.errorBars[figureCanvas, independentValues] = \
                        figureCanvas.axes.errorbar(X,Y, yerr=y_error, fmt=pointType)
                    #print self.errorBars
                    function_line, = figureCanvas.axes.loglog(Xtheory, Ytheory)
                    function_line.set_color(pointType[0])
                    function_line.set_marker('None')
                    function_line.set_linestyle('-')
                    self.functionLines[figureCanvas, independentValues] = function_line
                else:
                    self.dataPoints[figureCanvas, independentValues].set_data(X,Y)
                    self.errorBars[figureCanvas, independentValues].set_data(X,Y, yerr=y_error, fmt=pointType)
                    self.functionLines[figureCanvas, independentValues].set_data(Xtheory, Ytheory)
            else:
                if not self.isRunFitting:
                    function_line, = figureCanvas.axes.loglog(X, Ytheory, label=lb)
                    function_line.set_color(pointType[0])
                    marker, line = 'None', '-'
                    function_line.set_marker(marker)
                    function_line.set_linestyle(line)
                    self.functionLines[figureCanvas, independentValues] = function_line
                else:
                    self.functionLines[figureCanvas, independentValues].set_data(X, Ytheory)
        figureCanvas.axes.autoscale(True, tight=True)
        ax = figureCanvas.axes.axis()
        figureCanvas.axes.axis(getAxis(ax))
        #
        # Add the legend
        figureCanvas.axes.legend(loc=0)
        # Add titles
        if plotCollapse:
            figureCanvas.axes.set_xlabel(theory.XscaledLatex, \
                                         fontsize=FONTSIZEAXIS, labelpad = -5)
            figureCanvas.axes.set_ylabel(theory.YscaledLatex, fontsize=FONTSIZEAXIS)
            figureCanvas.axes.set_title(theory.scalingTitle)
        else:
            figureCanvas.axes.set_xlabel(theory.XLatex, fontsize=FONTSIZEAXIS)
            figureCanvas.axes.set_ylabel(theory.YLatex, fontsize=FONTSIZEAXIS)
            figureCanvas.axes.set_title(theory.title, fontsize=FONTSIZEAXIS)
        figureCanvas.draw()
        
        
    @QtCore.pyqtSignature("")
    def on_functionNewAction_triggered(self):
        form = editfunctiondlg.EditFunctionDlg(parent=self)
        form.show()
        if form.exec_():
            return

    @QtCore.pyqtSignature("")         
    def on_functionEditAction_triggered(self):
        selectFunction = SelectFunction("Select a function to edit:", self)
        if selectFunction.exec_():
            function = selectFunction.choice
            form = editfunctiondlg.EditFunctionDlg(function, parent=self)
            form.show()
            if form.exec_():
                return

    @QtCore.pyqtSignature("")         
    def on_functionDeleteAction_triggered(self):
        selectFunction = SelectFunction("Select a function to delete:", self)
        if selectFunction.exec_():
            function = selectFunction.choice
            msgTitle = "Delete a function"
            msg = "Are you sure to delete function %s?" % function
            if self.okToContinue(msgTitle, msg):
                filename = "%s.pkl" % function
                index = [filename in g for g in getPklFileNames].index(True)
                os.remove(getPklFileNames[index])

    @QtCore.pyqtSignature("")         
    def on_startFittingRunAction_triggered(self):
        if not self.isDataLoad:
            e = "Error: please first load data"
            QtGui.QMessageBox.warning(self, e, e)
            return
        #1. Call a widget to get:
        # initialParameters
        initialParameterValues = None
        # held Parameters
        #heldParams = [('sigma_k', 0.34)]
        #heldParams = [('H_c', 0.8), ('b', 1.05)]
        #heldParams = [('n', 0.65)]
        heldParams = None
        composite = self.compositeModule
        nModels = len(composite.models)
        if not self.isRunFitting:
            #2. Open new tabs: noCollapseTabNum + 1
            j = 0
            for k in range(nModels+1, nModels*2+1):
                setTab = "tab_%s" % k
                exec "self.%s = QtGui.QWidget()" % setTab
                exec "tab  = self.%s" % setTab
                tab.setObjectName(setTab)
                index = self.tabWidget.addTab(tab, "")
                self.tabWidget.setTabText(index, self.moduleNames[j]+"Coll")
                plotVBox = QtGui.QVBoxLayout(tab)
                figureCanvas = MplCanvas(tab)
                self.figureCanvas.append(figureCanvas)
                navToolBar = NavigationToolbar(figureCanvas, tab)
                self.navToolBar.append(navToolBar)
                plotVBox.addWidget(figureCanvas)
                plotVBox.addWidget(navToolBar)
                j = j+1
        # Start the fitting procedue
        t0 = time()
        # Unicode characters
        uniSymbol = {'tau': unichr(964), 'sigma_k': unichr(963)+"_k",\
                         'zeta': unichr(950)}
                    
        # Call holdFixedParams even if heldParams = None to check
        # if original Names and values have to be used
        composite.holdFixedParams(heldParams)
        if initialParameterValues is None:
            initialParameterValues = composite.theory.initialParameterValues

        print 'initial cost = ', composite.cost(initialParameterValues)
        out = composite.bestFit(initialParameterValues)
        
        print out[0]
        optimizedParameterValues = out[0]
        covar = out[1]
        errors = [covar[i,i]**0.5 for i in range(len(covar))]
        print 'optimized cost = ', composite.cost(optimizedParameterValues)
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
            zip(composite.theory.parameterNameList,optimizedParameterValues, errors):
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
        for i in range(nModels):
            model = composite.models[self.modelKeys[i]]
            data = model.data
            theory = model.theory
            # First add the fitting function to the existing data
            canvas = self.figureCanvas[i]
            self.plotDataAndFunction(canvas, data, theory, optimizedParameterValues, plotCollapse=None)
            # Now add data and the fitting function to the tabs containing the scaling collapse
            canvas = self.figureCanvas[i+nModels]
            self.plotDataAndFunction(canvas, data, theory, optimizedParameterValues, plotCollapse=True)
            
        ts = round(time() - t0, 3)
        print "*** Time elapsed:", ts
        self.isRunFitting = True
        #print self.errorBars

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())