import SloppyScaling
reload(SloppyScaling)
import WindowScalingInfo as WS
reload(WS)
import setupmodule as setMod

modules = {}

# Import the modules chosen in WindowScalingInfo
for moduleName in WS.moduleNames:
    mod_name = moduleName + "Module"
    exec("import "+ mod_name+" as "+moduleName)
    exec("reload ("+moduleName+")")
    
#for moduleName in WS.moduleNames:
    #modules[moduleName] = setMod.Module(moduleName)

jointModuleName = "".join(WS.moduleNames)

print jointModuleName
compositeModule = SloppyScaling.CompositeModel(jointModuleName)


for moduleName in WS.moduleNames:
    exec("obj_mod = "+moduleName)
    #exec("obj_mod = "+setMod.Module(moduleName))
    m = getattr(obj_mod,moduleName)
    #m = modules[moduleName]
    compositeModule.InstallModel(moduleName, m)