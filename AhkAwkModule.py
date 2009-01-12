import SloppyScaling
reload(SloppyScaling)

import AhkModule
reload(AhkModule)
import AwkModule
reload(AwkModule)

AhkAwk = SloppyScaling.CompositeModel('AhkAwk')
AhkAwk.InstallModel('Ahk', AhkModule.Ahk)
AhkAwk.InstallModel('Awk', AwkModule.Awk)

