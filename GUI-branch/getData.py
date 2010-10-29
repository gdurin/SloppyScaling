#!/usr/bin/env python
import os, sys
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import re
import numpy as np
import glob, pickle
from getFunctions import getFunctionNames
import ui_getData
import ui_datasetform

def getIndependentValues(fileName, independent, choice='min'):
    """
    Function able to automatically determine the independent parameters
    from fileName
    indepedent contains the independent parameters to extract
    The rules to construct the fileName are the following:
    * A function name (not used): for instance A00
    * An underscore "_" + the parameter name + the equal sign "=" and one or more values
      for instance: _W=1024 or _L=1024x512
    * Another underscore to finish the list of parameters
    Variable 'choice' sets how to choose the parameter if more than a value is present,
    as 'min', 'max', 'first', 'second', 'third'. If 'none' the first is taken
    Example:    choice = 'min' and L=1024x512 gives L = 512
    Example: 
    "A00_W=2048_k=40.96_L=8192x4096_KPZ.bnd" 
    gives
    "W,k,L" = (2048, 40.96, 4096)
    """
    independentList = independent.split(",")
    independentList = [i.strip() for i in independentList]
    values = [0]*len(independentList)
    # Selection of the parts to be analysed: yet to be fixed
    fileName, ext = os.path.splitext(fileName)
    selectParamsString = fileName.split("_")
    for string in selectParamsString:
        # Check if the string contains the =, i.e. it has a indep. parameter
        if "=" in string:
            param, value = string.split("=")
            if param in independent:
                index = independentList.index(param)
                match = re.findall("\d+\.?\d*", value)
                if len(match) == 1:
                    values[index] = (float(match[0]))
                else:
                    if choice == 'min':
                        values[index] = (float(min(match)))
                    elif choice == 'max':
                        values[index] = (float(max(match)))
                    elif choice == 'first':
                        values[index] = (float(match[0]))
                    elif choice == 'second':
                        values[index] = (float(match[1]))
                    elif choice == 'third':
                        values[index] = (float(match[2]))
                    else:
                        values.append(float(match[0]))
    print fileName
    print independent, tuple(values)
    return tuple(values)

class DataSetForm(QtGui.QWidget,ui_datasetform.Ui_Form):
    def __init__(self, parent=None):
        
        super(DataSetForm, self).__init__(parent)
        self.setupUi(self)
        
    
class InputDialog(QtGui.QDialog,ui_getData.Ui_Dialog):
    def __init__(self, myDir="./", parent=None):
    
        super(InputDialog, self).__init__(parent)
        self.myDir = myDir
        self.moduleNames = []
        self.independentValues = {}
        self.setupUi(self)
        self.dataSetForm_1 = DataSetForm(self.tab_1)
        
        self.getPklFileNames = getFunctionNames()
        for fName in sorted(self.getPklFileNames):
            self.dataSetForm_1.functionComboBox.addItem(fName)
        
        self.connect(self.dataSetForm_1.functionComboBox, \
                     QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.getFunctionIndependent)
        self.connect(self.dataSetForm_1.loadDataButton,\
                     QtCore.SIGNAL("clicked()"), self.loadData)
        
    def getFunctionIndependent(self, qstring):
        functionName =  str(qstring)
        try:
            F = open(self.getPklFileNames[functionName], 'rb')
            self.fvars = pickle.load(F)
        except:
            QtGui.QMessageBox.warning(self,"Error in the file",\
                                    "There is an error in the file : "+ functionName)
            return
        finally:
            self.independentNames = self.fvars['independentNames']
            self.dataSetForm_1.independentLineEdit.setText(self.independentNames)
            self.dataSetForm_1.independentLineEdit.setDisabled(True)

        
        #self.setGeometry(300, 300, 350, 80)
        #self.setWindowTitle('Load files')
        #self.independentValues = {}
        #self.myDir = myDir
        #self.independentNames = independentNames
    
    def loadData(self):
        fileDlg = QtGui.QFileDialog()
        self.files, other = fileDlg.getOpenFileNamesAndFilter(self, 'Select your file(s)', self.myDir)
        for filename in self.files:
            d, fileName = os.path.split(str(filename))
            values = getIndependentValues(fileName, self.independentNames)
            self.independentValues[values] = str(filename)
        
    def accept(self):
        current = str(self.dataSetForm_1.functionComboBox.currentText())
        print current
        self.moduleNames.append(current) 
        QtGui.QDialog.accept(self)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    independentNames = "D, H"
    myDir = "/home/gf/meas/Simulation/LIM"
    form =  InputDialog(myDir)
    form.show()
    sys.exit(app.exec_())
