import MayaColorTool as mct

#*****************************************************************************************
# START #*********************************************************************************
# function used to load tool inside programs such as Maya
def start_up():

    # If tool exists, reopen/show it. Else, create it.
    if 'tool' in globals():
        tool.toolsUI.show()
        tool.toolsUI.showNormal()
    # Not all users may remember to save changes every time they make a new color, 
    # so this prevents any temporary changes from being removed until the current maya session is closed.
    else:
        global tool
        tool = mct.MayaColorTool()
        tool.toolsUI.show()

start_up()