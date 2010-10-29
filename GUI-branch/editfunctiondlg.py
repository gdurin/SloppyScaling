#!/usr/bin/env python
import os, sys
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import matplotlib
import matplotlib.mathtext as mathtext
import string2latex as str2lx
from sympyUtils import getDiff
import pickle
import re
import ui_editfunctiondlg

MAC = "qt_mac_set_native_menubar" in dir()

def extractVariables(string,parent=None):
    """
    Find the X variable and the independent variables matching the form
    F(Xvariable|independentVariables) = .... 
    F(Xvariable) = .... 
    For instance:
    A__11(S|k,L,W) = ...
    gives:
    Xname = "S"
    Yname = "A__11"
    independent = "k,L,W"
    """
    try:
        string, Yvalue = string.split("=")
    except:
        e = "Error in the function"
        msg = "Please, check your function: the equal sign (=) is missing!"
        QtGui.QMessageBox.critical(parent,e,msg)
    if "|" in string:           
        string = string.strip()
        match = re.findall("\(.+\|.+\)",string)
        m = match[0]
        Xname, independent = m[1:-1].split("|") # This is fantastic!
        Yname = string.replace(m,"")
        #print Yname, Xname, independent
    else:
        match = re.findall("\(.+\)",string) 
        Xname = match[0][1:-1]
        Xname = Xname.strip()
        Yname = string.replace(match[0],"")
        Yname = Yname.strip()
        independent = ""
    Yvalue = Yvalue.strip()
    return Yname, Xname, independent, Yvalue
    
    
class EditLatexDlg(QtGui.QInputDialog):
    def __init__(self, text="", parent=None):
        """
        Dialog to edit a LaTeX string
        """
        super(EditLatexDlg, self).__init__(parent)
        title = "Edit the LaTeX equation"
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.adjustSize()
        self.setTextValue(text)
        self.setMinimumWidth(len(text)*10)
        self.setLabelText(title)
        self.setWindowTitle(title)

        
class EditFunctionDlg(QtGui.QDialog,ui_editfunctiondlg.Ui_editFunctionDialog):

    def __init__(self, functionName=None, parent=None):
        """
        Dialog class devoted to write/save a theoretical function
        """
        #
        # Initial setup
        #
        super(EditFunctionDlg, self).__init__(parent)
        self.setupUi(self)
        self.fvars = {}
        self.functionMessage = "Enter your function here"
        #
        # Check if working subdirectories exist:
        # images for latex images
        # files for pickle files, etc
        dirs = 'images','files','functions'
        self.dirImages, self.dirFiles,self.dirFunctions = dirs
        for d in dirs:
            if not os.path.isdir(d):
                os.path.os.mkdir(d)
        
        # Check if the pickle file exists
        # and load the variables' dictionary
        self.functionName = functionName
        if self.functionName:
            self.pklName = os.path.join(self.dirFunctions, self.functionName+".pkl")
            isPickleFile = os.path.exists(self.pklName)
            if isPickleFile:
                try:
                    F = open(self.pklName, 'rb')
                    self.fvars = pickle.load(F)
                except:
                    QtGui.QMessageBox.warning(self,"Error in the file",\
                                    "There is an error in the file : "+self.pklName)
                    sys.exit()
        else:
            isPickleFile = None

        # Populate the Widget
        # function section
        self.functionDefinitionText.setText(self.fvars.get('Ydefinition',self.functionMessage))
        self.functionDefinitionText.selectAll()
        self.functionDefinitionText.setFocus()
        self.functionDescriptionText.setText(self.fvars.get('YDescription',""))
        self.functionLatexText = self.fvars.get('YLatex',"")
        if self.functionLatexText:
            self.plotLatex(self.functionLatexText,self.functionLatexImage)
            self.functionLatexEditButton.setDisabled(False)
        else:
            self.functionLatexEditButton.setDisabled(True)
            self.functionLatexGuessButton.setDisabled(True)
        # Parameters
        self.indepedentText.setText(self.fvars.get('independentNames',""))
        self.indepedentText.setDisabled(True)
        self.parFittingText.setText(self.fvars.get('parameterNames',""))
        # Scaling variables
        _Xname = self.fvars.get('Xname',"X")
        _Yname = self.fvars.get('Yname',"Y") 
        _Wname = self.fvars.get('Wname',"")         
        self.varXLabel.setText(_Xname+":")
        self.varYLabel.setText(_Yname+":")
        _XscaledName = self.fvars.get('XscaledName',"")
        _YscaledName = self.fvars.get('YscaledName',"")
        _WscaledName = self.fvars.get('WscaledName',"")
        _XscaledValue = self.fvars.get('XscaledValue',"")
        _YscaledValue = self.fvars.get('YscaledValue',"")
        _WscaledValue = self.fvars.get('WscaledValue',"")
        self.varXLatexText = self.fvars.get('XscaledLatex',"")
        self.varYLatexText = self.fvars.get('YscaledLatex',"") 
        self.varWLatexText = self.fvars.get('WscaledLatex',"")         
        if _XscaledName:
            _varXscaledText = _XscaledName+" = " + _XscaledValue
            if self.varXLatexText:
                self.plotLatex(self.varXLatexText,self.varXLatexImage)
            self.varXLatexEditButton.setDisabled(False)
            self.varXLatexGuessButton.setDisabled(False)
        else:
            _varXscaledText = ""
            self.varXLatexEditButton.setDisabled(True)
            self.varXLatexGuessButton.setDisabled(True)
        self.varXScaledText.setText(_varXscaledText)
        # Do the same for Y
        if _YscaledName:
            _varYscaledText = _YscaledName+" = " + _YscaledValue
            if self.varYLatexText:
                self.plotLatex(self.varYLatexText,self.varYLatexImage)
            self.varYLatexEditButton.setDisabled(False)
            self.varYLatexGuessButton.setDisabled(False)
        else:
            _varYscaledText = ""
            self.varYLatexEditButton.setDisabled(True)
            self.varYLatexGuessButton.setDisabled(True)
        self.varYScaledText.setText(_varYscaledText)
        # Do the same for W
        if _WscaledName:
            _varWscaledText = _WscaledName+" = " + _WscaledValue
            if self.varWLatexText:
                self.plotLatex(self.varWLatexText,self.varWLatexImage)
            self.varWLatexEditButton.setDisabled(False)
            self.varWLatexGuessButton.setDisabled(False)
        else:
            _varWscaledText = ""
            self.varWLatexEditButton.setDisabled(True)
            self.varWLatexGuessButton.setDisabled(True)
        self.varWScaledText.setText(_varWscaledText)
        # Set the correction function
        self.correctionFunctionText.setText(self.fvars.get("Ycorrections",""))
        item = self.fvars.get("Ysign","*")
        itemPosition = self.correctionComboBox.findText(item)
        self.correctionComboBox.setCurrentIndex(itemPosition)
        self.correctionParamsText.setText(self.fvars.get("parameterNames_corrections",""))
        # set the Title
        if self.functionName:
            title = QtCore.QString("Edit function "+ self.functionName)
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("Edit a new function")

        
    def plotLatex(self,textLatex,where):
        imageFileName = str2lx.latex2Image(textLatex,thisDir=self.dirImages)
        if ".png" in imageFileName:
            image = QtGui.QImage()
            image.load(imageFileName)
            where.setPixmap(QtGui.QPixmap.fromImage(image))
            where.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
            where.show()
        else:
            QtGui.QMessageBox.warning(self,"Error in the LaTeX code",imageFileName)
        return    

    @QtCore.pyqtSignature("")
    def on_functionLatexGuessButton_clicked(self):
        text = str(self.functionDefinitionText.text())
        self.functionLatexText = str2lx.string2Latex(text)
        self.plotLatex(self.functionLatexText,self.functionLatexImage)
        self.functionLatexEditButton.setDisabled(False)
        
    @QtCore.pyqtSignature("")
    def on_varXLatexGuessButton_clicked(self):
        text = str(self.varXScaledText.text())
        self.varXLatexText = str2lx.string2Latex(text)
        self.plotLatex(self.varXLatexText,self.varXLatexImage)
        self.varXLatexEditButton.setDisabled(False)
        
    @QtCore.pyqtSignature("")
    def on_varYLatexGuessButton_clicked(self):
        text = str(self.varYScaledText.text())
        self.varYLatexText = str2lx.string2Latex(text)
        self.plotLatex(self.varYLatexText,self.varYLatexImage)
        self.varYLatexEditButton.setDisabled(False)
        
    @QtCore.pyqtSignature("")
    def on_varWLatexGuessButton_clicked(self):
        text = str(self.varWScaledText.text())
        self.varWLatexText = str2lx.string2Latex(text)
        self.plotLatex(self.varWLatexText,self.varWLatexImage)
        self.varWLatexEditButton.setDisabled(False)

    def editLatexCall(self,text,where):
        text = text[1:-1]
        inDialog = EditLatexDlg(text,self)
        if inDialog.exec_():
            string = inDialog.textValue()
            text = r'$'+str(string)+'$'
            self.plotLatex(text,where)
            return text
        
    ###################
    #### EditLatex slots   #####
    ###################
        
    @QtCore.pyqtSignature("")
    def on_functionLatexEditButton_clicked(self):
        text = self.functionLatexText
        where = self.functionLatexImage
        self.functionLatexText = self.editLatexCall(text,where)
            
    @QtCore.pyqtSignature("")
    def on_varXLatexEditButton_clicked(self):
        text = self.varXLatexText
        where = self.varXLatexImage
        self.varXLatexText = self.editLatexCall(text,where)
        
    @QtCore.pyqtSignature("")
    def on_varYLatexEditButton_clicked(self):
        text = self.varYLatexText
        where = self.varYLatexImage
        self.varYLatexText = self.editLatexCall(text,where)    
        
    @QtCore.pyqtSignature("")
    def on_varWLatexEditButton_clicked(self):
        text = self.varWLatexText
        where = self.varWLatexImage
        self.varWLatexText = self.editLatexCall(text,where)    
        
    ###################
    #### EditingFinished slots   #
    ###################
    @QtCore.pyqtSignature("")
    def on_functionDefinitionText_editingFinished(self):
        Y = self.functionDefinitionText.text()
        if Y != self.functionMessage:
            self.functionLatexGuessButton.setDisabled(False)
            fz =  str(self.functionDefinitionText.text())
            Yname, Xname, independent, Yvalue = extractVariables(fz,self)
            self.varXLabel.setText(Xname+":")
            self.varYLabel.setText(Yname+":")
            self.indepedentText.setText(independent)
            self.indepedentText.setDisabled(True)
            

    @QtCore.pyqtSignature("")
    def on_varXname_editingFinished(self):
        text = self.varXname.text()
        if text:
            _varXscaledText = self.varXScaledText.text()
            if _varXscaledText:
                _varXscaledText = text+_varXscaledText[1:]
            else:
                _varXscaledText = text+"_s = "
            self.varXLatexGuessButton.setDisabled(False)
        else:
            _varXscaledText = ""
            qArrows = QtCore.QString()
            self.varXLatexGuessButton.setDisabled(True)
        self.varXScaledText.setText(_varXscaledText)
        
    @QtCore.pyqtSignature("")
    def on_varXScaledText_editingFinished(self):
        _varXscaledText = self.varXScaledText.text()
        if _varXscaledText:
            self.varXLatexGuessButton.setDisabled(False)
        else:
            self.varXLatexGuessButton.setDisabled(True)            

    @QtCore.pyqtSignature("")
    def on_varWScaledText_editingFinished(self):
        _varWscaledText = self.varWScaledText.text()
        if _varWscaledText:
            self.varWLatexGuessButton.setDisabled(False)
        else:
            self.varWLatexGuessButton.setDisabled(True)            
        
    @QtCore.pyqtSignature("")
    def on_varYScaledText_editingFinished(self):
        _varYscaledText = self.varYScaledText.text()
        if _varYscaledText:
            self.varYLatexGuessButton.setDisabled(False)
        else:
            self.varYLatexGuessButton.setDisabled(True)   
            
    def accept(self):
        """
        Save the function's data into a pickle file
        """
        # Set the variables
        ### extract filename
        fz =  str(self.functionDefinitionText.text())
        self.fvars['Yname'],self.fvars['Xname'],  independent, self.fvars['Yvalue'] = \
            extractVariables(fz,self)
        self.fvars['XLatex'] = str2lx.string2Latex(self.fvars['Xname'])
        # Check if the name of the function passed to the class (functionName)
        # is the same given in the function definition
        # and set it to the latter if different
        if self.functionName != self.fvars['Yname']:
            nameSet = QtCore.QString("The new function name will be set to : "+self.fvars['Yname'])
            QtGui.QMessageBox.warning(self,nameSet, nameSet)
            self.pklName = os.path.join(self.dirFunctions,self.fvars['Yname']+".pkl")
            
        # Set the parameters
        self.fvars['independentNames'] = str(independent).replace(" ","")
        self.fvars['parameterNames'] = str(self.parFittingText.text()).replace(" ","")
        # Set the X scaling variables if present
        _varXscaledText = str(self.varXScaledText.text()).strip()
        if "=" in _varXscaledText:
            a,b = _varXscaledText.split("=")
            self.fvars['XscaledName'], self.fvars['XscaledValue'] = a.strip(),b.strip()
            try:
                self.fvars['XscaledLatex'] = self.varXLatexText
            except:
                Xerror = QtCore.QString("Error: please guess or enter a valid LaTeX string for variable ",self.fvars['XscaledName'])
                QMessageBox.critical(self,"Error in LaTeX", Xerror)
                self.varXLatexGuessButton.setFocus(True)
                return
        else:
            self.fvars['XscaledName'] = ""
            self.fvars['XscaledValue'] = ""
            self.fvars['XscaledLatex'] = ""
        # Other scaling variables
        _varWscaledText = str(self.varWScaledText.text()).strip()
        if "=" in _varWscaledText:
            a,b = _varWscaledText.split("=")
            self.fvars['WscaledName'], self.fvars['WscaledValue'] = a.strip(),b.strip()
            try:
                self.fvars['WscaledLatex'] = self.varWLatexText
            except:
                Werror = QtCore.QString("Error: please guess or enter a valid LaTeX string for variable ",self.fvars['WscaledName'])
                QMessageBox.critical(self,"Error in LaTeX", Werror)
                self.varWLatexGuessButton.setFocus(True)
                return
        else:
            self.fvars['WscaledName'] = ""
            self.fvars['WscaledValue'] = ""
            self.fvars['WscaledLatex'] = ""
        # Y variables
        self.fvars['Ydefinition'] = str(self.functionDefinitionText.text())
        self.fvars['YDescription'] = str(self.functionDescriptionText.text())
        self.fvars['YLatex'] = self.functionLatexText
        _varYscaledText = str(self.varYScaledText.text()).strip()
        if "=" in _varYscaledText:
            a,b = _varYscaledText.split("=")
            self.fvars['YscaledName'], self.fvars['YscaledValue'] = a.strip(),b.strip()
            try:
                self.fvars['YscaledLatex'] = self.varYLatexText
            except:
                Yerror = QtCore.QString("Error: please guess or enter a valid LaTeX string for variable ",self.fvars['YscaledName'])
                QMessageBox.critical(self,"Error in LaTeX", Yerror)
                self.varYLatexGuessButton.setFocus(True)
                return
        else:
            self.fvars['YscaledName'] = ""
            self.fvars['YscaledValue'] = ""        
            self.fvars['YscaledLatex'] =""

        self.fvars["Ysign"] = str(self.correctionComboBox.currentText())
        if self.fvars['Ysign'] == 'None':
            corrections_to_scaling = False
        else:
            corrections_to_scaling = True
        if corrections_to_scaling:
            self.fvars['Ycorrections'] = str(self.correctionFunctionText.text())
            self.fvars["parameterNames_corrections"] = str(self.correctionParamsText.text())
        #
        # Calcultate analytically the first derivative
        # 1. No corrections
        derivativeNoCorrections = {}
        params = self.fvars['parameterNames'].split(",")
        independent = self.fvars['independentNames'].split(",")
        allVariables = params + independent + [self.fvars['Xname']]
        Yvalue = self.fvars['Yvalue']
        XscaledName = self.fvars['XscaledName']
        if XscaledName:
            XscaledValue = self.fvars['XscaledValue']
            Yvalue = Yvalue.replace(XscaledName, "("+XscaledValue+")")
        WscaledName = self.fvars['WscaledName']
        if WscaledName:
            WscaledValue = self.fvars['WscaledValue']
            Yvalue = Yvalue.replace(WscaledName, "("+WscaledValue+")")
        diffs = getDiff(allVariables, Yvalue, params)
        for i,deriv in enumerate(diffs):
            derivativeNoCorrections[params[i]] = deriv
        self.fvars['derivNoCorrections'] = derivativeNoCorrections
        # 2. With corrections
        if corrections_to_scaling:
            derivativeWithCorrections = {}
            paramsCorrection = self.fvars["parameterNames_corrections"].split(",")
            params = params + paramsCorrection
            allVariables = allVariables + paramsCorrection
            allVariables = list(set(allVariables)) # Just to be sure
            Yvalue = " ".join([Yvalue,self.fvars['Ysign'],self.fvars['Ycorrections']])
            if XscaledName:
                XscaledValue = self.fvars['XscaledValue']
                Yvalue = Yvalue.replace(XscaledName, "("+XscaledValue+")")
            if WscaledName:
                WscaledValue = self.fvars['WscaledValue']
                Yvalue = Yvalue.replace(WscaledName, "("+WscaledValue+")")
            diffs = getDiff(allVariables, Yvalue, params)
            for i,deriv in enumerate(diffs):
                derivativeWithCorrections[params[i]] = deriv
            self.fvars['derivWithCorrections'] = derivativeWithCorrections
        # Set the title taken from the description
        self.fvars['title'] = self.fvars['YDescription']
        self.fvars['scalingTitle'] = self.fvars['YDescription']        
        # Save on disk
        F = open(self.pklName,'wb')
        pickle.dump(self.fvars,F)
        F.close()
        # Print for test only
        for key in self.fvars:
            print key, ": ", self.fvars[key]
            print 
        QtGui.QDialog.accept(self)   
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        fn = "A__11"
    form = EditFunctionDlg(fn)
    form.show()
    #callForm(form,'A11')
    sys.exit(app.exec_())

