#*****************************************************************************************
# Content: base class that programs like Maya can utilize for creating and applying colors 
#          to objects.
#
#
# version: 0.5
# date: 10/10/2020
#
# dependencies = QT
#
# To do's: 
#     > Create 'reload' action for 'file' menu to reload colors from json. 
#           (In case color gets accidentally deleted)
#
#*****************************************************************************************
import os
import sys
import json
import math
import colorsys
from decimal import Decimal
from functools import partial

from Qt import QtWidgets, QtGui, QtCore, QtCompat


#*****************************************************************************************
# VARIABLES
PATH = os.path.dirname(__file__)
JSON_PATH = r"{}\json\Qt_colors.json".format(PATH)


#*****************************************************************************************
# PARENT CLASS
class QtColorTool:

    def __init__(self):
        # BUILD local ui path
        # Gets the path for the ui file and builds the ui
        tool_ui_path = ("/").join([os.path.dirname(__file__), "ui", "Qt_colors.ui"])
        self.toolsUI = QtCompat.loadUi(tool_ui_path)

        # INITIAL SETTINGS #
        # These commands show the ui elements you should first see when you start the tool.
        self.toolsUI.colors_widget.show()
        self.toolsUI.colors_side_widget.show()

        # Preparing the error messages to be shown later for when the user does something wrong.
        self.toolsUI.color_name_error_message.hide()
        self.toolsUI.selected_color_error_message.hide()

        # Load in json data to variable so user can access and add new colors later on.
        self.saved_data = []
        with open(JSON_PATH) as json_file:
            self.saved_data = json.load(json_file)

        # INITIAL COLOR DATA #
        self.color_data = self.saved_data[0]
        self.color_buttons = {}
        self.color_names = []

        # Convert hsv color values (from 0-360, 0-100, 0-100) 
        # to read hsv in python    (to   0-1,   0-1,   0-255)
        self.hsv_correct_range =   [0.002777777,0.01,  2.55]

        # Puts the colors by name in a table for the user to select and delete from.
        self.delete_color_cell = {}
        self.total_color_rows = int(len(self.color_data)/3)
        if round((len(self.color_data)/3.0),4) > self.total_color_rows:
            self.total_color_rows+=1
        
        self.toolsUI.existing_colors_table.setRowCount(self.total_color_rows)

        # Creates the buttons used to change the color of selected object(s)
        for each in self.color_data:
            for key,value in each.items():
                self.color_names.append(key)
                self.build_color_button(each)
        # The Button to remove color from selected objects
        self.toolsUI.no_color_btn.clicked.connect(self.remove_color)
        
        # These allow the color sliders to actively change the color of 
        # color-preview ui elements to preview new color before officially creating it.
        self.toolsUI.hue_spinBox.valueChanged.connect(self.color_hsv_to_rgb)
        self.toolsUI.value_spinBox.valueChanged.connect(self.color_hsv_to_rgb)
        self.toolsUI.saturation_spinBox.valueChanged.connect(self.color_hsv_to_rgb)

        # Giving functionality to the "Add Color" and "Delete Color" Buttons
        self.toolsUI.create_color_button.clicked.connect(self.add_color)
        self.toolsUI.delete_color_button.clicked.connect(self.delete_color)

        # This Creates the Save features so a user can save their new or deleted colors.
        # This code is intended so that future features can be saved, like controllers and DG's
        self.save_options = ["colors"]
        self.save_menu = QtWidgets.QMenu("Save")
        self.toolsUI.file_menu.addMenu(self.save_menu)

        for each in self.save_options:
            action_number = self.save_options.index(each)
            self.save_options[action_number] = QtWidgets.QAction(each, self.save_menu)
            self.save_menu.addAction(self.save_options[action_number])
            self.save_options[action_number].triggered.connect(partial(self.save_changes,action_number))

        # Show the UI #
        self.toolsUI.show()


    #*************************************************************************************
    # MODIFY UI #*************************************************************************
    def build_color_button(self, color_dict):
        name = list(color_dict.keys())[0]
        values = color_dict[name]

        # Builds Button that can change the color of selected object(s)
        self.color_buttons[name] = QtWidgets.QPushButton(self.toolsUI)
        self.color_buttons[name].setObjectName(name)
        self.color_buttons[name].setMinimumHeight(45)
        self.toolsUI.colorButtons_grid.addWidget(self.color_buttons[name], 
                                                 math.floor((self.color_data.index(color_dict)/3)), 
                                                 self.color_data.index(color_dict)%3)
        self.color_buttons[name].clicked.connect(partial(self.change_color, 
                                                         values[0], 
                                                         values[1]))
        self.color_buttons[name].setStyleSheet("background-color: rgb({},{},{})".format(values[0][0]*255,
                                                                                        values[0][1]*255,
                                                                                        values[0][2]*255))
        # Adds the name of the specified color to a table in the 'Delete Color' tab for 
        # optional deletion by the user at a later time
        self.delete_color_cell[name] = QtWidgets.QTableWidgetItem(name)
        self.toolsUI.existing_colors_table.setItem(math.floor((self.color_data.index(color_dict)/3)),
                                                   self.color_data.index(color_dict)%3,
                                                   self.delete_color_cell[name])


    #*************************************************************************************
    # PRESS #*****************************************************************************

    # functions left open for a child class to modify depending on what 3D program is used.
    def change_color(self, scene_color, outliner_color):
        pass

    def remove_color(self):
        pass

    # Allows for colors added or deleted by user to become permanant changes.
    def save_changes(self, option=-1):
        if option == 0:
            self.saved_data[option] = self.color_data

        with open(JSON_PATH, "w") as json_file:
                json.dump(self.saved_data,json_file, sort_keys=True, indent=4)

    def add_color(self):
        new_color_name = self.toolsUI.color_new_name_lineEdit.text().lower()

        
        # If textfield for new color is left blank, or if name already exists:
        # Prints error message and new color is prevented from becoming a button.
        if new_color_name == "":
            print("Error: No name has been assigned to color.")
            self.toolsUI.color_name_error_message.setText("Error: No name has been assigned to color.")
            self.toolsUI.color_name_error_message.show()
            return
        elif new_color_name in self.color_names:
            print("Error: Color \"{}\" already exists. Choose new name.".format(new_color_name))
            self.toolsUI.color_name_error_message.setText("Error: Color \"{}\" already exists. Choose new name.".format(new_color_name))
            self.toolsUI.color_name_error_message.show()
            return
        else:
            self.toolsUI.color_name_error_message.hide()
        
        # get slider settings
        new_hue = self.toolsUI.hue_spinBox.value()
        new_value = self.toolsUI.value_spinBox.value()
        new_saturation = self.toolsUI.saturation_spinBox.value()

        new_color_values = colorsys.hsv_to_rgb(new_hue*self.hsv_correct_range[0], 
                                               new_saturation*self.hsv_correct_range[1], 
                                               new_value*self.hsv_correct_range[2])
        # finalizing new color information
        new_color_info = {new_color_name:[[round(new_color_values[0]/255, 4),
                                           round(new_color_values[1]/255, 4),
                                           round(new_color_values[2]/255, 4)], 
                                          [round(new_color_values[0]/255, 4),
                                           round(new_color_values[1]/255, 4),
                                           round(new_color_values[2]/255, 4)]]}
        self.color_data.append(new_color_info)
        self.color_names.append(new_color_name)
        
        # Creates a new row in 'Delete Color' Tab's table if not enough space for all created colors.
        if math.ceil(len(self.color_data)/3)==(len(self.color_data)/3):
            print("test1")
            self.total_color_rows+=1
            self.toolsUI.existing_colors_table.setRowCount(self.total_color_rows)
        
        # Creates a New Color Button
        self.build_color_button(new_color_info)

        # Remove color name from textfield after new color is created
        self.toolsUI.color_new_name_lineEdit.clear()


    def delete_color(self):
        # When existing color selected try deleting it, otherwise 
        # say no existing color was selected for deletion.
        try:
            color = QtWidgets.QTableWidgetItem.text(self.toolsUI.existing_colors_table.currentItem())
            self.toolsUI.selected_color_error_message.hide()
        except:
            print("Error: No Color was selected.")
            self.toolsUI.selected_color_error_message.show()
            return

        current_pos = [self.toolsUI.existing_colors_table.currentRow(),
                       self.toolsUI.existing_colors_table.currentColumn()]
        last_color_num =    self.color_names.index(self.color_names[-1])
        deleted_color_num = self.color_names.index(color)

        # Remove selected color's UI name from the "Delete Color" table, and corresponding colored button.
        self.toolsUI.existing_colors_table.takeItem(current_pos[0],current_pos[1])
        self.toolsUI.colorButtons_grid.removeWidget(self.color_buttons[color])
        self.color_buttons[color].deleteLater()

        # Moves proceeding names and buttons of deleted color to new positions 
        # in the color button ui, and the "Delete Color" Tab's table, removing any 
        # blank gaps between corresponding buttons and names.
        for each in self.color_names[deleted_color_num+1:last_color_num+1]:
            row = math.floor((self.color_names.index(each) / 3))
            column = self.color_names.index(each) % 3

            # removes the color button from the ui
            next_color_name = self.toolsUI.existing_colors_table.takeItem(row, column)
            self.toolsUI.colorButtons_grid.removeWidget(self.color_buttons[each])
            self.color_buttons[each].close()

            # add button back in
            if column == 0:
                row = row - 1
                column = 2
            else:
                column-=1
            self.toolsUI.existing_colors_table.setItem(row, column, next_color_name)
            self.toolsUI.colorButtons_grid.addWidget(self.color_buttons[each], row, column)
            self.color_buttons[each].show()

        # Removing excess empty rows in 'Delete Color' table
        if math.ceil(len(self.color_data)/3) != self.total_color_rows:
            self.total_color_rows = math.ceil(len(self.color_data)/3)
            self.toolsUI.existing_colors_table.setRowCount(self.total_color_rows)

        # Deletes temporary color information for selected color. Only lasts until tool is reloaded.
        # Note: When closed and reopened in Maya, changes are kept until Maya is closed and reopened.
        self.color_data.pop(deleted_color_num)
        self.color_names.pop(deleted_color_num)
        del self.color_buttons[color]
        

    # COLOR SETTINGS #********************************************************************
    # This allows for the text "Preview" and "Hidden", and the color preview box to 
    # actively change color when color sliders are moved back and forth.
    def color_hsv_to_rgb(self):
        hue = self.toolsUI.hue_slider.value()
        value = self.toolsUI.value_slider.value()
        saturation = self.toolsUI.saturation_slider.value()

        rgb_values = colorsys.hsv_to_rgb(hue*self.hsv_correct_range[0], 
                                         saturation*self.hsv_correct_range[1], 
                                         value*self.hsv_correct_range[2])

        # Directly changes the colors of the mentioned ui elements.
        self.toolsUI.hidden_label.setStyleSheet("color: rgb({},{},{})".format(rgb_values[0]*0.548,
                                                                              rgb_values[1]*0.548,
                                                                              rgb_values[2]*0.548))
        self.toolsUI.visible_label.setStyleSheet("color: rgb({},{},{})".format(rgb_values[0],
                                                                               rgb_values[1],
                                                                               rgb_values[2]))
        self.toolsUI.scene_display_frame.setStyleSheet("background-color: rgb({},{},{})".format(rgb_values[0],
                                                                                                rgb_values[1],
                                                                                                rgb_values[2]))
        

