import os
import scipy
import Utils
reload(Utils)

"""
Useful information about the WindowScaling data sets
"""

# Type of simulation: Linear, NonLinear etc
simulType = "NonLinear"

# Rows to skip
# Attention:
# Data are load entirely, but the fitting is done
# skipping the first 'rows_to_skip' lines
rows_to_skip = 4

# Type of normalization for the function (None, NormBasic, NormIntegerSum, NormLog)
# None does not need to be a string, NormBasic and NormIntegerSum do...
normalization = "NormBasic"

# Decide to add corrections to scaling in the function module (True/False)
corrections_to_scaling = False

# System Size (used to get the fileNames) and
# values of independent variables. (List of tuples if more than one)
#
#independentValues without window sizes...
#

Values = [\
         [1024,[0.001,0.005,0.01,0.05,0.1,1,10]],\
         [2048,[0.001,0.005]],\
         [4096,[0.0001,0.001,0.005]]\
         ]

#
#independentValues with window sizes
#
#List of curves with similar Ws
# Ws around 1.3
#independentValues=[(0.01, 1024, 128),(0.05, 1024, 64),(10,1024,8),(0.001,4096,512),(0.005,4096,256)] 
Ws1_3_list =  [\
            [1024,0.01,128],\
            [1024,0.05,64],\
            [1024,10,8],\
            [4096,0.001,512],\
            [4096,0.005,256]\
            ]
# Ws around 0.05
#independentValues = [(0.001, 1024, 16),(0.005, 1024, 8),(0.001,2048,16),(0.005, 2048,8),(0.0001,4096,64)]
Ws0_05_list =  [\
            [1024,0.001,16],\
            [1024,0.005,8],\
            [2048,0.001,16],\
            [2048,0.005,8],\
            [4096,0.0001,64]\
            ]
#Ws around 0.5
#independentValues = [(0.001,1024,128),(0.005,1024,64),(1,1024,8),(0.0001,4096,512)]
# Ws around 5
#independentValues = [(0.001, 1024, 1024),(0.005, 1024,512),(0.005, 4096, 1024),(0.001, 2048, 1024)]
# Ws LARGEST 30~170
#independentValues = [(1, 1024, 512),(10,1024,256),(1,1024,1024),(10,1024,512),(10,1024,1024)]

# for testing, large Ws and large k's
#independentValues = [(1,1024,256),(1,1024,512),(1,1024,1024),(10,1024,128),(10,1024,256),(10,1024,512),(10,1024,1024)]

# for testing, very small Ws...
#independentValues = [(0.001,1024,4),(0.001,2048,4),(0.001,4096,4)]

#independentValues = [(0.1,1024,8),(0.1,1024,16),(0.1,1024,32),(0.1,1024,64),(0.1,1024,128),(0.1,1024,256),(0.1,1024,512),(0.1,1024,1024)]


#List of curves with different Ws
#independentValues = [
#    (0.001, 2048, 8),(0.001,2048,256),
#    (0.005,1024,16),(0.05,1024,16),
#    (0.005, 1024,512),
#    (0.01,1024,64),(0.1,1024,64),
#    (0.005,4096,512)]
Ws_list = [\
            [1024,0.005,[16,512]],\
            [1024,0.05,16],\
            [1024,[0.01,0.1],64],\
            [2048,0.001,[8,256]],\
            [4096,0.005,512]\
            ]

#temp list of independentValues for jointModulerun (for making colors and symbols)
#independentValues = [(0.001, 1024, 16),(0.005, 1024, 8),(0.001,2048,16),(0.005, 2048,8),(0.0001,4096,64),(0.001, 2048, 8),(0.005,1024,16),(0.05,1024,16),(0.01,1024,64),(0.001,2048,256),(0.1,1024,64),(0.005,4096,512),(0.01, 1024, 128),(0.05, 1024, 64),(10,1024,8),(0.001,4096,512),(0.005,4096,256),(0.001,1024,1),(0.005,1024,1),(0.01,1024,1),(0.05,1024,1),(0.1,1024,1)]

# Using A00(system size) for A(s)
A00_list =  [\
            [1024,[0.001,0.005,0.01,0.05,0.1,1,10],1024],\
            [2048,[0.001,0.005],2048],\
            [4096,[0.0001,0.001,0.005],4096]\
            ]

# Using A10's and A01's (sorted according to win/corr)
A10_list = [\
            #[1024,[0.001,0.005,0.01,0.005,0.01,0.05,0.1,10],(4,1024)],\
            [2048,[0.001,0.005],(4,2048)],\
            [4096,[0.0001,0.001,0.005],(4,4096)]\
            ]

#The COMPLETE relevant list of (L,k,W) for A11
A11_list = [\
            [1024,0.001, (1,512)],\
            [1024,[0.005,0.01],(1,256)],\
            [1024,[0.05,0.1],(1,128)],\
            [1024,1,(1,32)],\
            [1024,10,(1,16)],\
            [2048,0.001,(2,512)],\
            [2048,0.005,(2,256)],\
            [4096,0.0001, (2,2048)],\
            [4096,[0.001,0.005],(2,512)]\
            ]
A11_W_1 = [\
           [1024, [0.001,0.005,0.01,0.05,0.1,1,10], 1]
          ]
A11_W_2 = [\
           [1024, [0.001,0.005,0.01,0.05,0.1,1,10], 2]
           ]
A11_W = [\
           [1024, [0.001,0.005,0.01,0.05,0.1,1,10], 1]
           ]


#The COMPLETE list of (k, L, W)
Complete_list = [\
            [1024, [0.001,0.005,0.01,0.05,0.1,0.5,1,10],(1,1024)],\
            [2048, [0.001,005],(1,2048)],\
            [4096, [0.0001,0.001,0.005],(1,4096)]\
            ]

sortedValues = False
independentNames, independentValues = Utils.get_independent(Values, sorting = sortedValues)

# Data to fit and models
moduleNames = ['Ahk','Awk']
#moduleNames = ['Ahk']
#moduleNames = ['A10', 'A11']
#moduleNames = ['A00']


# Directory where data to be fit is stored
# XXX We put all the different files into the same directory???
if os.getlogin() == 'yj':
    dataDirectory = "data/" #old data with problematic A10, and A01, but A11 are okay
    dataDirectory = "data02_18/" #fixed A10 and A01 files, and only A10 are binned
elif os.getlogin() == 'gf':
    dataDirectory = "/home/meas/WinSim/NonLinear/data/"

Symbol, Color = Utils.MakeSymbolsAndColors(independentValues)
