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
import os.path
from qgis.core import *
from qgis.gui import *
from qgis.gui import QgsMessageBar
from About import AboutDialog
from gui.generated.ui_Insta2QgisTool import Ui_Insta2QgisToolDialog
 
try:  
    import sys
    from instagram.client import InstagramAPI
    import requests ,base64 ,tempfile ,shutil
    from pydevd import *
except:
    None;
    
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
        self.settings.setValue("instagran2qgis/outpath", "")
 
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
        toolBar.setContextMenuPolicy(Qt.DefaultContextMenu)
        toolBar.setStyleSheet("QToolBar {border-bottom: 0px solid grey }")
        toolBar.setInputMethodHints(Qt.ImhNone)
        toolBar.setMovable(False)
        toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolBar.setFloatable(False)
        layout.addWidget(toolBar)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addStretch(0)
        self.setLayout(layout)
        return
 
    #Save Output file
    def SaveFile(self):
 
        out = QFileDialog.getSaveFileName(self, "Save Output", None,
                "shapefiles (*.shp);;All Files (*)")
  
        if out:
            if QFileInfo(out).suffix()=="":
                out += '.shp'
            
            self.output_cmb.setText(out)
            self.settings.setValue("instagran2qgis/outpath", out)
                
        return
 
    #Capture coord in map
    def captureCoord(self):
        self.hide()
        self.mapTool = CopyCoords(self.iface,parent=self)
        self.iface.mapCanvas().setMapTool(self.mapTool)
        return
  
    #Update value progessbar
    def update_progressbar(self, val):
        self.progressBar.setValue(val) 
         
    #Principal process
    def InstagramProcces(self):
        
        self.update_progressbar(50)
 
        access_token = self.lnToken.text()
        client_secret = self.lnAcces.text()
        user_id=self.lnId.text()
        count=self.sp_count.value()
        tag=self.ln_tags.text()
        
        #Put your values here for use.       
#         access_token =""
#         client_secret =""
 
        if not access_token:
            return 'Missing Access Token'
            
        try:
        
            api = InstagramAPI(access_token=access_token, client_secret=client_secret)
            tag_search, next_tag = api.tag_search(tag)
            tag_recent_media, next = api.tag_recent_media(count,tag_name=tag_search[0].name)
            
            categorized,layer=self.CreateShape()

            for tag_media in tag_recent_media: 
                self.AddFeatures(tag_media,layer,categorized)
 
            #Save layer in output path
            QgsVectorFileWriter.writeAsVectorFormat(layer,self.settings.value("instagran2qgis/outpath"), "CP1250", None, "ESRI Shapefile")
 
            self.update_progressbar(100)
            self.reject()
            
        except Exception, e:
            self.iface.messageBar().pushMessage("Error: ", "fail to load photos: "+str(e),level=QgsMessageBar.CRITICAL, duration=3) 
        return
 
    
    #Create shape
    def CreateShape(self): 
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'instagram_point', "memory")
        
        provider = layer.dataProvider()
        provider.addAttributes([QgsField("id", QVariant.String)])
        provider.addAttributes([QgsField("text", QVariant.String)])
        provider.addAttributes([QgsField("user", QVariant.String)])
        provider.addAttributes([QgsField("comments", QVariant.String)])
        provider.addAttributes([QgsField("likes_count", QVariant.Int)])
        provider.addAttributes([QgsField("created_time", QVariant.String)])
        provider.addAttributes([QgsField("type", QVariant.String)])
        provider.addAttributes([QgsField("latitude", QVariant.String)])
        provider.addAttributes([QgsField("longitude", QVariant.String)])
        provider.addAttributes([QgsField("tags", QVariant.String)])
        provider.addAttributes([QgsField("photo", QVariant.String)])
        provider.addAttributes([QgsField("video", QVariant.String)])
 
        layer.updateFields()
        
        categorized = []
        renderer = QgsCategorizedSymbolRendererV2("id", categorized)
        layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
 
        return categorized,layer
    
    #Add features to shape
    def AddFeatures(self,media,layer,categorized):
        
        #settrace()
        fet = QgsFeature()
        try: id = media.caption.id
        except: id =""
        
        try: text = media.caption.text
        except: text =""
        try: user = media.caption.user.full_name
        except: user =""
        try: comments = str(media.comments).strip('[]')
        except: comments =""
        try: likes_count = media.like_count
        except: likes_count =""
        try: created_time = media.created_time.now().strftime("%Y-%m-%d %H:%M:%S")
        except: created_time =""
        try: type = media.type
        except: type =""
        try: latitude = media.location.point.latitude
        except: latitude =""
        try: longitude = media.location.point.longitude
        except: longitude =""
        try: tags = str(media.tags).strip('[]')
        except: tags =""      
        try: photo = media.get_thumbnail_url()
        except: photo =""
        try: video = media.videos['standard_resolution'].url
        except: video =""
        
        if longitude!="":
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(longitude),float(latitude))))
 
        fet.setAttributes([id,text, user, comments,likes_count, created_time,type, latitude, longitude,  tags, photo,video])
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
         
        data2 = requests.get(thumb, stream=True).content   
        base64data = base64.b64encode(data2).replace('\n','')
        base64String = '<image xlink:href="data:image/png;base64,{0}" width="240" height="240" x="0" y="0" />'.format(base64data)
        path =tempfile.gettempdir() + os.sep + media.caption.id + '_i.jpg.svg'
        with open(path, 'w') as f:
            f.write( startSvgTag + base64String + endSvgTag)
   
        svgStyle = {}
        svgStyle['fill'] = '#0000ff'
        svgStyle['name'] = tempfile.gettempdir() + os.sep + media.caption.id + '_i.jpg.svg'
        svgStyle['outline'] = '#000000'
        svgStyle['size'] = '30'
        sym_image = QgsSvgMarkerSymbolLayerV2.create(svgStyle)
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        symbol.changeSymbolLayer(0, sym_image)
        new_category = QgsRendererCategoryV2(str(media.caption.id), symbol,str(media.caption.id))
        categorized.append(new_category)
        renderer = QgsCategorizedSymbolRendererV2(media.caption.id, categorized)
        layer.setRendererV2(renderer)
        
        layer.updateExtents()
        layer.triggerRepaint()
        
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
