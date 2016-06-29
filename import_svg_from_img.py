from xml.dom import minidom
import re

from osgeo import ( gdal, ogr, osr )
from gdalconst import GA_ReadOnly

def getPolygonFeature(nameFile):
  def getStringCoords(s):
    s_coords = []
    id = 0
    while True:
      id += 1
      idx = s.find('C')
      if idx == -1:
        break
      s = s[ idx + 2 : ]
      idx = s.find('Z')
      #
      s_coords.append( s[ : idx - 1 ] )
      #
      s = s[ idx + 2 : ]
    #
    return s_coords
  #
  # Read SVG
  doc = minidom.parse( nameFile )
  s = doc.getElementsByTagName('path')[0].getAttribute('d')
  doc.unlink()
  #
  s_coords = getStringCoords( s )
  polygons = []
  for s in s_coords:
    line = [ map( lambda v: float( v ), item.split(',') )  for item in re.findall( r'\d+\.\d+\,\d+\.\d+', s) ]
    line.insert( 0, line[-1] )
    polygons.append( line )
  #
  return polygons

def getParamsImage( fileImage ):
  ds = gdal.Open( fileImage, GA_ReadOnly )
  wkt = ds.GetProjection()
  geoTransf = ds.GetGeoTransform()
  del ds
  ds = None
  #
  srs = osr.SpatialReference()
  return { 
    'tiePoint': ( geoTransf[0], geoTransf[3] ),
    'resX': geoTransf[1], 'resX': -1*geoTransf[5],
    'srs': srs.ImportFromWkt( wkt )
   }
  #
  return ( srs, tiePoint )

def offsetPolygonFeature(polygonFeat, tiePoint, resX, resY):
  for item in polygonFeat:
  


fileSVG = '/home/lmotta/temp/1.svg'
polygonFeat = getPolygonFeature( fileSVG )
#
fileImage = '/home/lmotta/temp/1.tif'
( srs, tiePoint ) = getCrsTiepoint( fileImage )
#

