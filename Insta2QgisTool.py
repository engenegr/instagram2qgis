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

from About import AboutDialog
from Insta2QgisDialog import Insta2QgisDialog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import gui.generated.resources_rc
from qgis.core import *
 
try:
    import sys
    from pydevd import *
except:
    None
    

class Insta2QgisTool:

    """QGIS Plugin Implementation."""
    
    def __init__(self, iface):
        
        """Constructor."""
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale//userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'Instragram2qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
 
    def initGui(self):
        self.action = QAction(QIcon(":/imgInstragram/images/icon.png"), u"Instragram2qgis", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Instragram2qgis", self.action)
       
        self.actionAbout = QAction(QIcon(":/imgInstragram/images/info.png"), u"About", self.iface.mainWindow())
        self.iface.addPluginToMenu(u"&Instragram2qgis", self.actionAbout)
        self.actionAbout.triggered.connect(self.About)


    def unload(self):
        self.iface.removePluginMenu(u"&Instragram2qgis", self.action)
        self.iface.removePluginMenu(u"&Instragram2qgis", self.actionAbout)
        self.iface.removeToolBarIcon(self.action)

    def About(self):
        self.About = AboutDialog(self.iface)
        self.About.exec_()
        return
    
    def run(self):
        self.dlg = Insta2QgisDialog(self.iface)
        self.dlg.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint) 
        self.dlg.exec_()