# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Instagram to Qgis
                                 A QGIS plugin
 Search and downloading Instagram images and create a point shapefile with them.
                             -------------------
        begin                : 2016-03-13
        copyright            : (C) 2016 All4Gis.
        email                : franka1986@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
""" 
import os.path
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .gui.generated.About import Ui_About
from qgis.core import *
from qgis.gui import *
 
try:
    import sys
    from pydevd import *
except:
    pass

 
class AboutDialog(QDialog, Ui_About):
    def __init__(self, iface):      
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__) 
        self.video = self.plugin_dir + '//example//ExampleUse.mp4'
    
    # Video de ejemplo
    def ShowVideo(self): 
        if os.path.exists(self.video):
             
            if sys.platform.startswith('dar'):
                subprocess.call(['open', self.video])
            elif sys.platform.startswith('lin'):
                subprocess.call(['xdg-open', self.video])
            elif sys.platform.startswith('win'):
                os.startfile(self.video)
            else:   
                pass
             
        else:
            self.iface.messageBar().pushMessage("Error: ", "Could not open video file: " + self.video, level=QgsMessageBar.CRITICAL, duration=3) 
            return