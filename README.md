# Instagram to Qgis

This plugin allows to import data from instagram and visualize it in Qgis.

In order to do so, a points-type shapefile is created with the geolocalized images downloaded from instagram according to the parameters introduced by the user.

The images can be downloaded by the following parameters:
- Tag
- For coordinates,...

####This first version only allows to download by tag.####
	
[Example](https://github.com/All4Gis/instagram2qgis/example)

## Prerequisites

The following libraries must be installed:
- instagram
- httplib2
- requests	
- simplejson
- six 

You can download them here,[additional libraries](https://github.com/All4Gis/instagram2qgis/lib)

You also need an "ACCESS TOKEN" and an "ACCESS CLIENT". To obtain them, you must create an application with your instagram account.
[Instragram app](https://www.instagram.com/developer/register/),

Once created, a “CLIENT ID” and a “CLIENT SECRET” will be provided and you can create the “ACCESS TOKEN" by accessing the following link [enlace](http://instagram.pixelunion.net/)


 
[© All4gis 2016]




