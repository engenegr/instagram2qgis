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
#from PyQt4 import Qt
#from PyQt4.QtCore import QSettings,QSize,QFileInfo,QVariant
#from PyQt4.QtGui import QDialog,QVBoxLayout,QToolBar,QFileDialog,QCursor,QPixmap,QMessageBox
#from qgis.core import QgsMapLayerRegistry,QgsSvgMarkerSymbolLayerV2,QgsFeature,QgsVectorFileWriter,QgsPoint,QgsCoordinateTransform,QgsField,QgsVectorLayer,QgsRendererCategoryV2,QgsGeometry,QgsCategorizedSymbolRendererV2,QgsAction,QgsMapTool,QgsCoordinateReferenceSystem,QgsSymbolV2,QgsCoordinateReferenceSystem,QgsMessageBar
 
import os.path
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from About import AboutDialog
from gui.generated.ui_Insta2QgisTool import Ui_Insta2QgisToolDialog
 
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
        self.settings = QSettings()
        self.settings.setValue("instagram2qgis/outpath", "")
 
        width=600
        height=450
        
        self.setMinimumSize(QSize(width, height))
        self.setMaximumSize(QSize(width, height))
        
        self.AddAboutButton()
        self.HideGroupBox()
        
        self.TypeSearch="hashtags" #Default search
 
    #Hide groupbox
    def HideGroupBox(self):
        self.groupBox_user.hide()
        self.groupBox_location.hide()
        self.groupBox_popular.hide()
        self.groupBox_location_id.hide()
        return
     
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
 
    #Capture coords in map
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
        
        self.HideGroupBox()
        self.groupBox_tags.hide()
        self.sp_count.hide() 
        self.label_4.hide()
 
        sender = self.sender().objectName()
        
        if(value):
            
            if sender == "ch_hashtags":
                self.groupBox_tags.show()
                self.sp_count.show()  
                self.label_4.show() 
                self.TypeSearch="hashtags" 
                               
            elif sender == "ch_user":
                self.lnId.setPlaceholderText("Instagram")  
                self.label_3.setText("User name")  
                self.groupBox_user.show()
                self.TypeSearch="user"   
                           
            elif sender == "ch_location":
                self.groupBox_location.show()
                self.TypeSearch="coords" 
                            
            elif sender == "ch_popular":
                self.groupBox_popular.show()
                self.TypeSearch="popular"
                
            elif sender == "ch_user_recent":
                self.groupBox_popular.show()
                self.TypeSearch="user_recent"
                
            elif sender == "ch_user_media":
                self.groupBox_popular.show()
                self.TypeSearch="user_media"
                
            elif sender == "ch_location_recent":
                self.groupBox_location_id.show()
                self.TypeSearch="location_recent"
                
            elif sender == "ch_user_follow":
                self.lnId.setPlaceholderText("25025320")   
                self.label_3.setText("User ID")            
                self.groupBox_user.show()
                self.TypeSearch="user_follow"
        return
         
    #Principal process
    def InstagramProcces(self):
        
        self.aceptar.setCursor(QCursor(Qt.ForbiddenCursor))
        self.update_progressbar(10)
        
        access_token = self.lnToken.text()
        client_secret = self.lnAcces.text()
        user_id=self.lnId.text()
 
        #Put your values here for use.       
#         access_token =""
#         client_secret =""
 
        if not access_token or not client_secret:
            QMessageBox.information(self, "Empty values", "Complete mandatory items <access_token> and <client_secret>", QMessageBox.AcceptRole)
            return  
        try:
            api = InstagramAPI(access_token=access_token, client_secret=client_secret)
 
            #Search recent media with Tag       
            if self.TypeSearch=="hashtags":
                count=self.sp_count.value()  
                tag=self.ln_tags.text()
                #tag="Madrid"
                if tag=="":
                    QMessageBox.information(self, "Empty values", "Tag value is empty", QMessageBox.AcceptRole)
                    self.aceptar.setCursor(QCursor(Qt.PointingHandCursor))
                    self.update_progressbar(0)
                    return  
            
                tag_search, next_tag = api.tag_search(tag)
                tag_recent_media, next = api.tag_recent_media(count,tag_name=tag_search[0].name)
                
                #return self.Checklength() if len(tag_recent_media)==0 else [self.AddFeatures(tag_media,layer,categorized) for tag_media in tag_recent_media]
                 
                if len(tag_recent_media)==0:return self.Checklength()
                categorized,layer=self.CreateShape()
                for tag_media in tag_recent_media: 
                    self.AddFeatures(tag_media,layer,categorized)
                    
            #Search recent media with Location              
            elif self.TypeSearch=="coords":
                #Search with Location
                lat=self.ln_lat.text()
                lng=self.ln_lng.text()
                distance=self.sp_distance.value()                    
                location_search =api.media_search(lat=str(lat),lng=str(lng), distance=int(distance))  

                if len(location_search)==0:return self.Checklength()
                categorized,layer=self.CreateShape()
                for location in location_search:
                    self.AddFeatures(location,layer,categorized)          
  
            #Search recent media with user 
            elif self.TypeSearch=="user":                
                if self.lnId.text()=="":
                    QMessageBox.information(self, "Empty values", "User name value is empty", QMessageBox.AcceptRole)
                    self.aceptar.setCursor(QCursor(Qt.PointingHandCursor))
                    self.update_progressbar(0)
                    return
                
                user_name=self.lnId.text()
                #user_name="Instagram"
                user_search = api.user_search(user_name)

                if len(user_search)==0:return self.Checklength()
                layer=self.CreateShapeMin()
                for user in user_search:
                    self.AddFeaturesMin(user,layer)   

            #Search user recent 
            elif self.TypeSearch=="user_recent": 
                recent_media, next = api.user_recent_media()

                if len(recent_media)==0:return self.Checklength() 
                categorized,layer=self.CreateShape()
                for media in recent_media:
                    self.AddFeatures(media,layer,categorized) 
                          
            #Search User Media Feed    
            elif self.TypeSearch=="user_media":            
                media_feed, next = api.user_media_feed()

                if len(media_feed)==0:return self.Checklength() 
                categorized,layer=self.CreateShape()
                for media in media_feed:
                    self.AddFeatures(media,layer,categorized) 
            
            #Search User follow
            elif self.TypeSearch=="user_follow":
                #user_id="25025320"
                if self.lnId.text()=="":
                    QMessageBox.information(self, "Empty values", "User ID value is empty", QMessageBox.AcceptRole)
                    self.aceptar.setCursor(QCursor(Qt.PointingHandCursor))
                    self.update_progressbar(0)
                    return 
                
                user_follows, next = api.user_follows(user_id)
                
                if len(user_follows)==0:return self.Checklength()
                layer=self.CreateShapeMin()
                for user in user_follows:
                    self.AddFeaturesMin(user,layer) 
             
            #Search Location recent
            elif self.TypeSearch=="location_recent":
                
                if self.ln_loc_id.text()=="":
                    QMessageBox.information(self, "Empty values", "Location ID value is empty", QMessageBox.AcceptRole)
                    self.aceptar.setCursor(QCursor(Qt.PointingHandCursor))
                    self.update_progressbar(0)
                    return  

                location_id=int(self.ln_loc_id.text())
                #location_id=514276
                recent_media, next = api.location_recent_media(location_id=location_id)
                
                if len(recent_media)==0:return self.Checklength()
                categorized,layer=self.CreateShape()
                for media in recent_media:
                    self.AddFeatures(media,layer,categorized)
 
            #Search recent popular 
            elif self.TypeSearch=="popular": 
                media_search = api.media_popular()
                
                if len(media_search)==0:return self.Checklength() 
                categorized,layer=self.CreateShape()
                for media in media_search:
                    self.AddFeatures(media,layer,categorized)  
  
            #Save layer in output path
            QgsVectorFileWriter.writeAsVectorFormat(layer,self.settings.value("instagram2qgis/outpath"), "CP1250", None, "ESRI Shapefile")
 
            self.update_progressbar(100)

            self.aceptar.setCursor(QCursor(Qt.PointingHandCursor))
 
            self.reject()
            
        except Exception, e:
            self.iface.messageBar().pushMessage("Error: ", "fail to load photos: "+str(e),level=QgsMessageBar.CRITICAL, duration=20)             
            self.aceptar.setCursor(QCursor(Qt.PointingHandCursor))
             
        return
 
    #Message length media
    def Checklength(self):
        self.iface.messageBar().pushMessage("Error: ", "No photos available,please try again",level=QgsMessageBar.INFO, duration=3)
        self.update_progressbar(0)
        self.aceptar.setCursor(QCursor(Qt.PointingHandCursor))
        return
    
    #Create shape for media min
    def CreateShapeMin(self): 
        
        self.update_progressbar(20)        
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'instagram_point', "memory")
        provider = layer.dataProvider()
        provider.addAttributes([QgsField("user_id", QVariant.Int)])
        provider.addAttributes([QgsField("user_name", QVariant.String)])
        provider.addAttributes([QgsField("user_full_name", QVariant.String)])
        provider.addAttributes([QgsField("user_profile_picture", QVariant.String)])
 
        layer.updateFields()
 
        self.update_progressbar(30)
 
        self.AddActions(layer)       
 
        #Add Layer to canvas
        QgsMapLayerRegistry.instance().addMapLayer(layer)
 
        return layer  
    
    #Add features to shape
    def AddFeaturesMin(self,media,layer):
         
        self.update_progressbar(40)
        fet = QgsFeature()
        
        try: user_id = media.id
        except: user_id =""
        try: user_name = media.username
        except: user_name =""
        try: user_full_name = media.full_name
        except: user_full_name =""
        try: user_profile_picture = media.profile_picture
        except: user_profile_picture =""
 
        fet.setAttributes([user_id,user_name,user_full_name,user_profile_picture])
        pr = layer.dataProvider()
        pr.addFeatures([fet])
 
        return
                          
    #Create shape
    def CreateShape(self): 
        
        self.update_progressbar(20)
        
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'instagram_point', "memory")
        
        provider = layer.dataProvider()
        provider.addAttributes([QgsField("id_photo", QVariant.String)])
        provider.addAttributes([QgsField("text", QVariant.String)])
        provider.addAttributes([QgsField("user_name", QVariant.String)])
        provider.addAttributes([QgsField("user_full_name", QVariant.String)])
        provider.addAttributes([QgsField("user_id", QVariant.Int)])
        provider.addAttributes([QgsField("user_profile_picture", QVariant.String)])
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
 
        self.update_progressbar(30)

        categorized = []
        renderer = QgsCategorizedSymbolRendererV2("id_photo", categorized)
        layer.setRendererV2(renderer)
        
        self.AddActions(layer)       
 
        #Add Layer to canvas
        QgsMapLayerRegistry.instance().addMapLayer(layer)
 
        return  categorized,layer
    
    def AddActions(self,layer):
        #Add actions layers to open video and photo
        actions = layer.actions()   
        actions.addAction(QgsAction.OpenUrl, 'Open photo in browser', '[% "photo" %]')
        actions.addAction(QgsAction.OpenUrl, 'Open video in browser', '[% "video" %]')       
        actions.addAction(QgsAction.OpenUrl, 'Open link profile in browser', '[% "link_profile" %]')   
        
        return
    
    #Add features to shape
    def AddFeatures(self,media,layer,categorized):
         
        self.update_progressbar(40)
        fet = QgsFeature()
        try: id_photo = media.id
        except: id_photo =""     
        try: text = media.caption.text
        except: text =""
        try: user_name = media.caption.user.username
        except: user_name =""
        try: user_full_name = media.caption.user.full_name
        except: user_full_name =""
        try: user_id = media.caption.user.id
        except: user_id =""
        try: user_profile_picture = media.caption.user.profile_picture
        except: user_profile_picture =""
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
        try: media_type = media.type
        except: media_type =""
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
 
        fet.setAttributes([id_photo,text, user_name,user_full_name,user_id,user_profile_picture,comments,comments_count,likes_count, created_time,link_profile,media_type, latitude, longitude,  tags, photo,video])
        pr = layer.dataProvider()
        pr.addFeatures([fet])
        
        self.CreateMarker(categorized,media,photo,layer)
        
        return
    
    #Create marker with instagram photo
    def CreateMarker(self,categorized,media,thumb,layer):
        self.update_progressbar(50) 
               
        startSvgTag = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg><g>"""
        endSvgTag = """ </g></svg>"""
         
        data = requests.get(thumb, stream=True).content   
        base64data = base64.b64encode(data).replace('\n','')
        base64String = '<image xlink:href="data:image/png;base64,{0}" width="320" height="240"/>'.format(base64data)
        
        if self.settings.value("instagram2qgis/outpath")=="" :
            path =tempfile.gettempdir() + os.sep + media.id + '.jpg.svg'
        else:
            #Icons
            p=QFileInfo(self.settings.value("instagram2qgis/outpath")).path()+ os.sep 
            svgpath = p + "instagram_svg"
            if not os.path.exists(svgpath): 
                os.makedirs(svgpath)
            path = svgpath + os.sep + media.id + '.jpg.svg'
            #Style
            qmlpath = p +"instagram_qml"
            if not os.path.exists(qmlpath): 
                os.makedirs(qmlpath)
 
        with open(path, 'w') as f:
            f.write( startSvgTag + base64String + endSvgTag)
   
        svgStyle = {}
        
        svgStyle['name'] = path 
        svgStyle['size'] = '30'
        sym_image = QgsSvgMarkerSymbolLayerV2.create(svgStyle)
        
        symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        symbol.changeSymbolLayer(0, sym_image)
        new_category = QgsRendererCategoryV2(str(media.id), symbol,str(media.id))
        categorized.append(new_category)
        renderer = QgsCategorizedSymbolRendererV2("id_photo", categorized)
        layer.setRendererV2(renderer)
        
        layer.updateExtents()
        layer.triggerRepaint()
       
        
        try:#Save style Layer
            layer.saveNamedStyle(qmlpath + os.sep +'instagram_style.qml')
        except:
            None
        
        self.update_progressbar(75) 
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
