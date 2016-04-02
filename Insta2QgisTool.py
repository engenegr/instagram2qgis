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
import os.path, shutil

from About import AboutDialog
from Insta2QgisDialog import Insta2QgisDialog
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import gui.generated.resources_rc
from qgis.core import *
from qgis.gui import *

class Insta2QgisTool:

    """QGIS Plugin Implementation."""
    
    def __init__(self, iface):
        
        """Constructor."""
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale//userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'Instagram2qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
 
    def initGui(self):
        self.action = QAction(QIcon(":/imgInstagram/images/icon.png"), u"Instagram2qgis", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Instagram2qgis", self.action)
       
        self.actionAbout = QAction(QIcon(":/imgInstagram/images/info.png"), u"About", self.iface.mainWindow())
        self.iface.addPluginToMenu(u"&Instagram2qgis", self.actionAbout)
        self.actionAbout.triggered.connect(self.About)


    def unload(self):
        self.iface.removePluginMenu(u"&Instagram2qgis", self.action)
        self.iface.removePluginMenu(u"&Instagram2qgis", self.actionAbout)
        self.iface.removeToolBarIcon(self.action)

    def About(self):
        self.About = AboutDialog(self.iface)
        self.About.exec_()
        return
    
    def run(self):
        self.Prerequisites()#Check libraries
        self.dlg = Insta2QgisDialog(self.iface)
        self.dlg.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint) 
        self.dlg.exec_()
        
    def tr(self, message):
        return QCoreApplication.translate('Instagram2qgis', message)  
       
    #Check Prerequisites
    def Prerequisites(self):
        try:
            from instagram.client import InstagramAPI
            import requests,httplib2,simplejson,six
        except ImportError:
            plugin_dir = os.path.dirname(__file__).replace("\\", "/")+"/lib"          
            prefixPath=QgsApplication.prefixPath().replace("\\", "/")+"/python"        
            ret = QMessageBox.question(None, self.tr("Missing libraries!"), 
                                    self.tr("The missing libraries can be found at: \n\n'"+plugin_dir+"'\n\n"+
                                    "You must copy them to:\n\n"+
                                     "'"+prefixPath+"'\n\n"
                                     +"Do you want to copy the libraries automatically?\n\n"),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                                     
            if ret == QMessageBox.Yes:
                
                self.copyDirectory(plugin_dir.replace("/", "\\")+"\\instagram", prefixPath.replace("/", "\\")+"\\instagram","instagram")
                self.copyDirectory(plugin_dir.replace("/", "\\")+"\\httplib2", prefixPath.replace("/", "\\")+"\\httplib2","httplib2")
                self.copyDirectory(plugin_dir.replace("/", "\\")+"\\requests", prefixPath.replace("/", "\\")+"\\requests","requests")
                self.copyDirectory(plugin_dir.replace("/", "\\")+"\\simplejson", prefixPath.replace("/", "\\")+"\\simplejson","simplejson")
                self.copyDirectory(plugin_dir.replace("/", "\\")+"\\six", prefixPath.replace("/", "\\")+"\\six","six")
                
                return
            if ret == QMessageBox.No:
                self.iface.messageBar().pushMessage("Warning: ", "Remember to copy the missing libraries manually" ,level=QgsMessageBar.INFO, duration=3) 
                return
        return
    
    #Copy libs
    def copyDirectory(self,src, dest,name):
        src=src+"\\"
        dest=dest+"\\"
        try:
            shutil.copytree(src, dest)
            self.iface.messageBar().pushMessage("Warning: ", "Libraries  "+name+" copied satisfactorily" ,level=QgsMessageBar.INFO, duration=3)
        # Directories are the same
        except shutil.Error as e:
            self.iface.messageBar().pushMessage("Error: ", "Library not copied.Directories are the same. Error: %s" % e, level=QgsMessageBar.CRITICAL, duration=3)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            self.iface.messageBar().pushMessage("Error: ", "Library not copied. Error: %s" % e, level=QgsMessageBar.CRITICAL, duration=3)
        