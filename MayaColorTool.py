#*****************************************************************************************
# Content: Child class built for Maya to utilize custom color coder
#
#
# version: 0.1
# date: 10/10/2020
#
# dependencies = QT, PySide2, colors
#
#
#*****************************************************************************************
import os
import sys
import json
from functools import partial

from maya import cmds
from maya import OpenMayaUI as omui 

from Qt import QtCompat
from PySide2.QtGui import *
from PySide2.QtCore import * 
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import QtColorTool as qct


#*****************************************************************************************
# VARIABLES
PATH = os.path.dirname(__file__)
JSON_PATH = r"{}\json\Qt_colors.json".format(PATH)

# Calling Maya Main Window as Pyside2 Widget
# Prevents tool from being moved behind main maya window while interacting with Maya.
MAYA_MAIN_WINDOW_PTR = omui.MQtUtil.mainWindow()
MAYA_MAIN_WINDOW = wrapInstance(long(MAYA_MAIN_WINDOW_PTR), QWidget) 


#*****************************************************************************************
# CHILD CLASS
class MayaColorTool(qct.QtColorTool):
    
    def __init__(self):
        
        # NOTE: This old style parent class call is intended for programs that use Python 2.7
        #       super() does not work.
        qct.QtColorTool.__init__(self)


        # Parents the tool under Maya main window, preventing it from being moved behind maya.
        self.toolsUI.setParent(MAYA_MAIN_WINDOW)        
        self.toolsUI.setWindowFlags(Qt.Window)

        # Variable used to convert color values from json file into format used within maya.
        self.hsv_correct_range = [0.002777777,0.01,2.55]

        # SHOW the UI #
        self.toolsUI.show()
        
    #*************************************************************************************
    # PRESS #*****************************************************************************
    # Reformatted functions so Maya can add or remove colors from selected object(s)
    def change_color(self,scene_color, outliner_color):
        selection = cmds.ls(selection=True)

        for name in selection: 
            shapes = cmds.listRelatives(name, path=True, shapes=True)

            # set color of object in maya Outliner
            cmds.setAttr("{}.useOutlinerColor".format(name), True)
            cmds.setAttr("{}.outlinerColor".format(name), 
                         outliner_color[0],
                         outliner_color[1], 
                         outliner_color[2]) 
                 
            # set color of object in maya Scene
            # This prevents the user from making the color of child controls from changing in 
            # the scene, unless it is an object similar to a joint, which has no child shapes.
            if shapes == None: 
                cmds.setAttr("{}.overrideEnabled".format(name), True)
                cmds.setAttr("{}.overrideRGBColors".format(name), True)
                cmds.setAttr("{}.overrideColorRGB".format(name), 
                             scene_color[0], 
                             scene_color[1], 
                             scene_color[2]) 
            else:
                for each in shapes:
                    cmds.setAttr("{}.overrideEnabled".format(each), True)
                    cmds.setAttr("{}.overrideRGBColors".format(each), True)
                    cmds.setAttr("{}.overrideColorRGB".format(each), 
                                 scene_color[0], 
                                 scene_color[1], 
                                 scene_color[2]) 

    def remove_color(self):
        selection = cmds.ls(selection = True)
    
        # disable color in the maya Outliner
        for name in selection: 
            cmds.setAttr("{}.useOutlinerColor".format(name ), False)
            shapes = cmds.listRelatives(name, 
                                        shapes=True, 
                                        path=True)
            if shapes == None:
                cmds.setAttr("{}.overrideEnabled".format(name), False)
            # disable color in the maya Scene
            elif shapes != None:
                for each in shapes: 
                    cmds.setAttr("{}.overrideEnabled".format(each), False)


