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
import re
from .About import AboutDialog
from .Insta2QgisDialog import Insta2QgisDialog
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#import .gui.generated.resources_rc
from qgis.core import *
from qgis.gui import *
from qgis.utils import reloadPlugin
try:  
    import sys
    from pydevd import *
except:
    pass 

class Insta2QgisTool:

    """QGIS Plugin Implementation."""
    
    def __init__(self, iface):
        
        """Constructor."""
        
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value("locale//userLocale")[0:2]
        self.instaladas=False
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
    
    def run(self):
        #Check libraries
        self.Prerequisites()
        self.Prerequisites("requests") 
        self.Prerequisites("httplib2") 
        self.Prerequisites("simplejson")
        self.Prerequisites("six") 
        
        if self.instaladas==True:
            reloadPlugin('instagram2qgis')
            return
            
        self.dlg = Insta2QgisDialog(self.iface)
        self.dlg.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint) 
        self.dlg.exec_()
        
    def tr(self, message):
        return QCoreApplication.translate('Instagram2qgis', message)  
       
    #Check Prerequisites
    def Prerequisites(self,name=None):
        try:
            if name==None:
                name="instagram"
                from instagram.client import InstagramAPI
            elif name=="requests":
                import requests
            elif name=="httplib2":
                import httplib2
            elif name=="simplejson":
                import simplejson
            elif name=="six":
                import six
        except:
            lib_dir = os.path.normpath(self.plugin_dir +QDir.separator()+"lib")
            
            if sys.platform.startswith('win'):    
                prefixPath=os.path.normpath(QgsApplication.prefixPath()+QDir.separator()+"python")
            else:
                prefixPath=os.path.normpath(QgsApplication.prefixPath()+QDir.separator()+"share//qgis//python")   
                 
            lib_dir =re.sub("\\\\","//",lib_dir) 
            prefixPath= re.sub("\\\\","//",prefixPath) 
            
            ret = QMessageBox.question(None, self.tr("Missing library "+name+" !"), 
                                    self.tr("The missing library can be found at: \n\n'"+lib_dir+"'\n\n"+
                                    "You must copy them to:\n\n"+
                                     "'"+prefixPath+"'\n\n"
                                     +"Do you want to copy the library "+name+" automatically?\n\n"),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                                     
            if ret == QMessageBox.Yes:                            
                self.copyDirectory(lib_dir +"//" + name, prefixPath+"//"+name , name)
                self.instaladas = True
                return
            if ret == QMessageBox.No:
                self.iface.messageBar().pushMessage("Warning: ", "Remember to copy the missing libraries manually" ,level=QgsMessageBar.INFO, duration=3) 
                return
        return
 
    #Copy libs
    def copyDirectory(self,src, dest,name):
        src=src+"//"
        dest=dest+"//"
        try:
            shutil.copytree(src, dest)
            self.iface.messageBar().pushMessage("Warning: ", "Libraries  "+name+" copied satisfactorily" ,level=QgsMessageBar.INFO, duration=3)
        # Directories are the same
        except shutil.Error as e:
            self.iface.messageBar().pushMessage("Error: ", "Library not copied.Directories are the same. Error: %s" % e, level=QgsMessageBar.CRITICAL, duration=3)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            self.iface.messageBar().pushMessage("Error: ", "Library not copied. Error: %s" % e, level=QgsMessageBar.CRITICAL, duration=3)
        