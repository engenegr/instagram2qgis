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
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import os.path
from qgis.core import *
from qgis.gui import *
from About import AboutDialog
from gui.generated.ui_Insta2QgisTool import Ui_Insta2QgisToolDialog
from pip.cmdoptions import src
 
try:  
    import sys
    from pydevd import *
    from instagram.client import InstagramAPI
    import base64 ,tempfile,requests
except:
    None
    
class Insta2QgisDialog(QDialog, Ui_Insta2QgisToolDialog):
    
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        
        """Constructor."""
        
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.canvas=self.iface.mapCanvas()
        self.AddAboutButton()
        self.settings = QSettings()
        self.settings.setValue("instagram2qgis/outpath", "")
        
        self.groupBox_user.hide()
        self.groupBox_location.hide()
        self.groupBox_popular.hide()
        
        self.setMinimumSize(QtCore.QSize(600, 350))
        self.setMaximumSize(QtCore.QSize(600, 350))
        
        self.TypeSearch="tag" #Default search
 

    # About
    def about(self):
        self.About = AboutDialog(self.iface)
        self.About.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.About.exec_()
        return

    #Add About button
    def AddAboutButton(self):
        layout = QVBoxLayout()
        toolBar = QToolBar(self)
        toolBar.addAction(u"About", self.about)         
        toolBar.setStyleSheet("QToolBar {border-bottom: 0px solid grey }")
        layout.addWidget(toolBar)
        self.setLayout(layout)
        return
 
    #Save Output file
    def SaveFile(self):
        out = QFileDialog.getSaveFileName(self, "Save Output", None,"shapefiles (*.shp);;All Files (*)") 
        if out:
            if QFileInfo(out).suffix()=="":
                out += '.shp'
            
            self.output_cmb.setText(out)
            self.settings.setValue("instagram2qgis/outpath", out)           
        return 
    
    #Get values of list Tags
    def GetListTags(self,list):       
        values=[]
        for i ,val in enumerate(list):
            values.append(str(list[i].name)) 
        return str(values).strip('[]')
 
    #Capture coord in map
    def captureCoord(self):
        self.hide()
        self.mapTool = CopyCoords(self.iface,parent=self)
        self.iface.mapCanvas().setMapTool(self.mapTool)
        return
  
    #Update value progessbar
    def update_progressbar(self, val):
        self.progressBar.setValue(val) 
        
    #Toggle GroupBox
    def TypeSearch(self,value):
        self.groupBox_user.hide()
        self.groupBox_location.hide()
        self.groupBox_tags.hide()
        self.groupBox_popular.hide()     
        
        sender = self.sender().objectName()
        if(value):
            if sender == "ch_hashtags":
                self.groupBox_tags.show()   
                self.TypeSearch="tag"                
            elif sender == "ch_user":
                self.groupBox_user.show()
                self.TypeSearch="user"              
            elif sender == "ch_location":
                self.groupBox_location.show()
                self.TypeSearch="location"             
            elif sender == "ch_popular":
                self.groupBox_popular.show()
                self.TypeSearch="popular"
                return
        
        return
         
    #Principal process
    def InstagramProcces(self):
 
        self.aceptar.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.aceptar.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        
        access_token = self.lnToken.text()
        client_secret = self.lnAcces.text()
        user_id=self.lnId.text()
 
        #Put your values here for use.       
#         access_token =""
#         client_secret =""

 
        if not access_token or not client_secret:
            QtGui.QMessageBox.information(self, "Empty values", "Complete mandatory items <access_token> and <client_secret>", QtGui.QMessageBox.AcceptRole)
            return  
        try:
            count=self.sp_count.value() 
            self.update_progressbar(50)
            
            api = InstagramAPI(access_token=access_token, client_secret=client_secret)

            categorized,layer=self.CreateShape()
            #Search recent media with Tag       
            if self.TypeSearch=="tag":
                 
                tag=self.ln_tags.text()
                
                tag_search, next_tag = api.tag_search(tag)
                tag_recent_media, next = api.tag_recent_media(count,tag_name=tag_search[0].name)
 
                if len(tag_recent_media)==0:
                    self.iface.messageBar().pushMessage("Error: ", "No photos available,please try again"+str(e),level=QgsMessageBar.INFO, duration=3) 
                    return
 
                for tag_media in tag_recent_media: 
                    self.AddFeatures(tag_media,layer,categorized)
                    
            #Search recent media with Location              
            elif self.TypeSearch=="location":
                #Search with Location
                lat=self.ln_lat.text()
                lng=self.ln_lng.text()
                distance=self.sp_distance.value()                    
                location_search =api.media_search(lat=str(lat),lng=str(lng), distance=int(distance))  
                if len(location_search)==0:
                    self.iface.messageBar().pushMessage("Error: ", "No photos available,please try again"+str(e),level=QgsMessageBar.INFO, duration=3) 
                    return
                
                for location in location_search:
                    self.AddFeatures(location,layer,categorized)          
 
            #Search recent media with user 
            elif self.TypeSearch=="user":
                user_id=self.lnId.text()
                user_search = api.user_search(q=user_id)
                
                if len(user_search)==0:
                    self.iface.messageBar().pushMessage("Error: ", "No photos available,please try again"+str(e),level=QgsMessageBar.INFO, duration=3) 
                    return
                
                for user in user_search:
                    self.AddFeatures(user,layer,categorized)   

            #Search recent popular 
            elif self.TypeSearch=="popular":
                 
                media_search = api.media_popular()
                
                if len(media_search)==0:
                    self.iface.messageBar().pushMessage("Error: ", "No photos available,please try again"+str(e),level=QgsMessageBar.INFO, duration=3) 
                    return
                
                for media in media_search:
                    self.AddFeatures(media,layer,categorized)  
                           
                    
            #Save layer in output path
            QgsVectorFileWriter.writeAsVectorFormat(layer,self.settings.value("instagram2qgis/outpath"), "CP1250", None, "ESRI Shapefile")
 
            self.update_progressbar(100)

            self.aceptar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.aceptar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor)) 
            
            self.reject()
            
        except Exception, e:
            self.iface.messageBar().pushMessage("Error: ", "fail to load photos: "+str(e),level=QgsMessageBar.CRITICAL, duration=3) 
            
            self.aceptar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.aceptar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        return
 
    
    #Create shape
    def CreateShape(self): 
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'instagram_point', "memory")
        
        provider = layer.dataProvider()
        provider.addAttributes([QgsField("id", QVariant.String)])
        provider.addAttributes([QgsField("text", QVariant.String)])
        provider.addAttributes([QgsField("user", QVariant.String)])
        provider.addAttributes([QgsField("comments", QVariant.String)])
        provider.addAttributes([QgsField("comments_count", QVariant.Int)])
        provider.addAttributes([QgsField("likes_count", QVariant.Int)])
        provider.addAttributes([QgsField("created_time", QVariant.Date)])
        provider.addAttributes([QgsField("link_profile", QVariant.String)])
        provider.addAttributes([QgsField("type", QVariant.String)])
        provider.addAttributes([QgsField("latitude", QVariant.Double)])
        provider.addAttributes([QgsField("longitude", QVariant.Double)])
        provider.addAttributes([QgsField("tags", QVariant.String)])
        provider.addAttributes([QgsField("photo", QVariant.String)])
        provider.addAttributes([QgsField("video", QVariant.String)])
 
        layer.updateFields()
 
        self.update_progressbar(50)

        categorized = []
        renderer = QgsCategorizedSymbolRendererV2("id", categorized)
        layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
 
        return  categorized,layer
    
    #Add features to shape
    def AddFeatures(self,media,layer,categorized):
 
        fet = QgsFeature()
        try: id = media.id
        except: id =""     
        try: text = media.caption.text
        except: text =""
        try: user = media.caption.user.full_name
        except: user =""
        try: comments = str(media.comments).strip('[]')
        except: comments =""
        try: comments_count = media.comments_count
        except: comments_count =""
        try: likes_count = media.like_count
        except: likes_count =""
        try: created_time = media.created_time.now().strftime("%Y-%m-%d %H:%M:%S")
        except: created_time =""
        try: link_profile = media.link
        except: link_profile =""
        try: type = media.type
        except: type =""
        try: latitude = media.location.point.latitude
        except: latitude =""
        try: longitude = media.location.point.longitude
        except: longitude =""
        try: tags = self.GetListTags(media.tags)
        except: tags =""      
        try: photo = media.get_thumbnail_url()
        except: photo =""
        try: video = media.videos['standard_resolution'].url
        except: video =""
        
        if longitude!="":
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(longitude),float(latitude))))
 
        fet.setAttributes([id,text, user, comments,comments_count,likes_count, created_time,link_profile,type, latitude, longitude,  tags, photo,video])
        pr = layer.dataProvider()
        pr.addFeatures([fet])
        
        self.CreateMarker(categorized,media,photo,layer)
        
        return
    
    #Create marker with instagram photo
    def CreateMarker(self,categorized,media,thumb,layer):
        self.update_progressbar(75) 
               
        startSvgTag = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg><g>"""
        
        endSvgTag = """ </g></svg>"""
         
        data = requests.get(thumb, stream=True).content   
        base64data = base64.b64encode(data).replace('\n','')
        base64String = '<image xlink:href="data:image/png;base64,{0}" width="320" height="240"/>'.format(base64data)
        
        if self.settings.value("instagram2qgis/outpath")=="" :
            path =tempfile.gettempdir() + os.sep + media.id + '_i.jpg.svg'
        else:
            #Icons
            p=QFileInfo(self.settings.value("instagram2qgis/outpath")).path()+ os.sep 
            svgpath = p + "instagram_svg"
            if not os.path.exists(svgpath): 
                os.makedirs(svgpath)
            path = svgpath + os.sep + media.id + '_i.jpg.svg'
            #Style
            qmlpath = p +"instagram_qml"
            if not os.path.exists(qmlpath): 
                os.makedirs(qmlpath)
 
        with open(path, 'w') as f:
            f.write( startSvgTag + base64String + endSvgTag)
   
        svgStyle = {}
        #svgStyle['fill'] = '#0000ff'
        svgStyle['name'] = path
        #svgStyle['outline'] = '#000000'
        svgStyle['size'] = '30'
        sym_image = QgsSvgMarkerSymbolLayerV2.create(svgStyle)
        
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        symbol.changeSymbolLayer(0, sym_image)
        new_category = QgsRendererCategoryV2(str(media.id), symbol,str(media.id))
        categorized.append(new_category)
        renderer = QgsCategorizedSymbolRendererV2("id", categorized)
        layer.setRendererV2(renderer)
        
        layer.updateExtents()
        layer.triggerRepaint()
       
        
        try:#Save style Layer
            layer.saveNamedStyle(qmlpath + os.sep +'instagram_style.qml')
        except:
            None
        
        return
        

#Copy coord canvas class
class CopyCoords(QgsMapTool):
    def __init__(self, iface,parent=None):
        QgsMapTool.__init__(self, iface.mapCanvas())   
        self.canvas = iface.mapCanvas()
        self.iface = iface
        self.parent=parent

        self.cursor = QCursor(QPixmap(["16 16 3 1",
                    "      c None",
                    ".     c #FF0000",
                    "+     c #FFFFFF",
                    "                ",
                    "       +.+      ",
                    "      ++.++     ",
                    "     +.....+    ",
                    "    +.     .+   ",
                    "   +.   .   .+  ",
                    "  +.    .    .+ ",
                    " ++.    .    .++",
                    " ... ...+... ...",
                    " ++.    .    .++",
                    "  +.    .    .+ ",
                    "   +.   .   .+  ",
                    "   ++.     .+   ",
                    "    ++.....+    ",
                    "      ++.++     ",
                    "       +.+      "]))

    def activate(self):
        self.canvas.setCursor(self.cursor)
    
    def canvasReleaseEvent(self, event):

        crsSrc = self.canvas.mapRenderer().destinationCrs()
        crsWGS = QgsCoordinateReferenceSystem(4326)
        
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
    
        #Convert coords to EPSG:4326
        xtrans = QgsCoordinateTransform(crsSrc, crsWGS)
        point = xtrans.transform(QgsPoint(point.x(),point.y()))
 
        self.parent.ln_lat.setText(str(point.x()));
        self.parent.ln_lng.setText(str(point.y()));
        self.iface.mapCanvas().unsetMapTool(self.parent.mapTool)
        self.parent.exec_()
