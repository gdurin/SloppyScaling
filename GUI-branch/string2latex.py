#!/usr/bin/env python ##################
########################################
# This script translates a string into a LaTeX string
# and makes an image.png
# Author: Gianfranco Durin
# Date: 2010-09-16
########################################

import os
import matplotlib
import matplotlib.pylab as mpl
import matplotlib.mathtext as mathtext
import re
import copy

def findElement(element, string):
    return [match.start() for match in re.finditer(re.escape(element), string)]

def findParentheses(string):
    """
    Get a dictionary of matching parenthesis where: 
    the key is the position of the left parenthesis "("
    and the value parenthesis[left] is the position of the right parenthesis ")"
    """
    parentheses = {}
    parLeft = findElement("(", string)
    parRight = findElement(")", string)
    parLeft.reverse() # This does the trick to quickly find the match
    for left in parLeft:
        right = min([i for i in parRight if i>left])
        parentheses[left] = right
        parRight.remove(right)
    return parentheses

def parentheses2curly(positions, string):
    """
    Change the parentheses () into curly brakets {}
    """
    t = list(string)
    p1, p2 = positions
    t[p1], t[p2] = "{", "}"
    return "".join([ i for i in t])

def addSlash(string):
    return "\\"+str(string)

def string2Latex(string):
    """
    Transform a string into a LaTeX expression
    """
    # 0. Check if "**1.0*" exists and erase it:
    # a usual result from sympy differentials
    exprex = ["**1.0*","**1.*"]
    for expr in exprex:
        if expr in string:
            string = string.replace(expr,"*")        
    # 1. Numbers with dots (es. 1.0 -> 1)
    match = re.findall("\d+\.\d+[^0-9]|\d+\.[^0-9]",string)
    if match:
        for syb in match:
            str_n, after = syb[:-1],syb[-1:]
            n = float(str_n)
            if n == 1. and after == "*":
                string = string.replace(syb,"")
            elif n == int(n):
                string = string.replace(syb,str(int(n))+after)
    # 2. Selected commands which require to change 
    # parentheses to curly brakets
    commands = {"**":"^", "sqrt":"\sqrt"}
    for cm in commands:
        cm_found = findElement(cm,string)
        parentheses = findParentheses(string)        
        if cm_found:
            for pos in cm_found:
                p = pos + len(cm) # check if there is a "(" after the command
                if p in parentheses:
                    positions = p,parentheses[p]
                    string = parentheses2curly(positions,string)
                if cm == "**": # chech if there is a number after it
                    match = re.search(r'\*\*\d+\.\d+',string)
                    if match:
                        gr = match.group()
                        if type(gr).__name__ == 'str':
                            gr = [gr]
                        for g in gr:
                            rep = g[:2]+"{"+g[2:]+"}"
                            string = string.replace(g,rep)
            string = string.replace(cm,commands[cm])
    # 2b. Remove "*", or add space if " * "
    match = re.findall('\s\*\s',string)
    for m in match:
        string = string.replace(m,"\/")    
    string = string.replace("*"," ")
    if match:
        string = string.replace("*","\/")    
    # 3. Greek letters
    # REMEMBER: shortest letter before the others, such as eta, beta, zeta
    greeks = ['alpha','chi','delta','iota','lambda','mu','nu','omega',\
              'psi','tau','upsilon','xi']
    greeksTuples = [('eta','beta','zeta'),('gamma','digamma'),\
                    ('epsilon', 'varepsilon'),('kappa','varkappa'),\
                    ('phi','varphi'),('pi','varpi'),('rho','varrho'),\
                    ('sigma','varsigma'),('theta','vartheta')] 
    # Not ambigous letters
    for i in range(2):
        for g in greeks:
            if i==1:g = g.capitalize()
            if g in string:
                string = string.replace(g,addSlash(g))
    # Now deal with ambigous letters
    gPositions = {}            
    for i in range(2):
        for g in greeksTuples:
            g0 = g[0]
            if i==1: g0 = g0.capitalize()
            find_g0 = findElement(g0,string)
            # Check if the shortest letter is present
            if find_g0:
                # Then collect the position of the other letters, if present
                for g1 in g[1:]:
                    if i==1: g1 = g1.capitalize()
                    g1Pos= findElement(g1,string)
                    if g1Pos:
                        gPositions[g1] = g1Pos
                        delta = len(g1) - len(g0)
                        for pos in g1Pos:
                            if pos+delta in find_g0:
                                find_g0.remove(pos+delta)
                gPositions[g0] = find_g0 
    # At this point we have the true positions of g0 and g1
    stringList = list(string)
    for gr in gPositions:
        pos = gPositions[gr]
        for p in pos:
            stringList[p] = "\\"+stringList[p]
    string = "".join(stringList)
    # 4. Underscore
    match = re.findall('__\w\w|___\w\w\w',string)
    for m in match:
        n = m.count("_")
        sub = "_{"+m[-n:]+"}"
        string = string.replace(m, sub)
    # 5. calA -> \cal{A}
    match = re.findall('cal\w',string)
    for m in match:
        sub = "\mathcal{"+m[-1]+"}"
        string = string.replace(m, sub)
    ############################
    return r'$'+string+'$'

def latex2Image(latexString,n='0000',thisDir="./"):
    """
    Return a fileName of the image if no errors occur,
    otherwise return an error string
    """
    try:
        fileName = 'eqn'+str(n)+'.png'
        fileName = os.path.join(thisDir,fileName)
        parser = mathtext.MathTextParser("Bitmap")
        parser.to_png(fileName, latexString, fontsize=16, dpi=100)
        return fileName
    except matplotlib.pyparsing.ParseFatalException:
        error =  "There is an error in your LaTeX commands"
        return error

def string2Image(string,n='0000',thisDir="./"):
    """
    Return the filename of an image starting from a string
    """
    latex = string2Latex(string)
    return latex2Image(latex,n,thisDir)

def showLatexImage(latexString,n='0000',thisDir="./"):
    fileName =  latex2Image(latexString,n,thisDir)
    if ".png" in fileName:
        os.system('okular '+fileName+" \&")
    else:
        print fileName
    return

def showLatexFromString(string,n='0000',thisDir="./"):
    latex = string2Latex(string)
    showLatexImage(latex,n,thisDir)
    return

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        s = sys.argv[1]
    else:
        #s = "((1.0*k/L)**(sigma_k*Gamma))**((2.-tau)*(1.+zeta))*s**(1.-tau+1./(eta+zeta))/W*exp(-(S_s*(Iy_0+Iy_1*W*(1.0*k/L)**(sigma_k)))**n)"
        s = r"(s*(k/L)**(sigma_k*(1.+beta)))**(2.-tau) /s * exp(-(S_s*Ix_s)**ns+U_0)"
        #s = "rho(lambda|T) = (8*pi*h*c)/lambda**5 * (exp(h*c/(k*T*lambda))-1)**(-1)"
        s = "3.0*alpha**2 + 1.0*eta_0 + 2.*zeta_0 **(sqrt(2.5*eta)*1.*beta) + 4*gamma"
        s = "P(S|W) = alpha**2 + eta * (S/W)**1.5 * exp(-(S/S_0)**2.5)"
        #s = "S_s**((2.-tau)*(1.+zeta)/zeta)/s*exp(-1.0*S_s**n_h*Ix_h)"
        s = "calA__11 * S_s**((2.-tau)*(1.+zeta)/zeta)/s * exp(-1.0*S_s**n*Ix_h)"
        #s = "S**1.0*(1/S)"
    myDir = "images"
    sLatex = string2Latex(s)
    print sLatex
    showLatexImage(sLatex,thisDir=myDir)
    #im = string2Image(s)
    #print im