import SloppyScaling
reload(SloppyScaling)
import WindowScalingInfo as WS
reload(WS)

# Import the modules chosen in WindowScalingInfo
for moduleName in WS.moduleNames:
    mod_name = moduleName + "Module"
    exec("import "+ mod_name+" as "+moduleName)
    exec("reload ("+moduleName+")")

jointModuleName = "".join(WS.moduleNames)

jointModule = SloppyScaling.CompositeModel(jointModuleName)
for moduleName in WS.moduleNames:
    exec("obj_mod = "+moduleName)
    m = getattr(obj_mod,moduleName)
    jointModule.InstallModel(moduleName, m)

