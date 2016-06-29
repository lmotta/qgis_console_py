## 2016-05-22

from PyQt4 import ( QtGui, QtCore )
from qgis import ( core as QgsCore, gui as QgsGui )

from osgeo import gdal
from gdalconst import GA_Update

import numpy as np


class CurrentBlockImage(QtCore.QObject):
  def __init__(self, iface):
    super(CurrentBlockImage, self).__init__()
    self.iface = iface
    self.canvas = iface.mapCanvas()
    self.titleMsg = "Current Block Image"
    self.msgError = None
    self.paramsImgView = self.resX = self.resY = None
    self.blockImage = None
    self.isTypeBlockProvider = True
    self._connect()
    #
    self.setLayer( self.iface.activeLayer() )

  def __del__(self):
    self._connect( False )
    if not self.blockImage is None:
      del self.blockImage
    self.blockImage = None

  def _connect(self, isConnect = True):
    ss = [
      { 'signal': self.canvas.currentLayerChanged, 'slot': self.setLayer },
      { 'signal': self.canvas.destinationCrsChanged, 'slot': self.setParamsImageView },
      { 'signal': self.canvas.extentsChanged, 'slot': self.setParamsImageView  }
    ]
    if isConnect:
      self.hasConnect = True
      for item in ss:
        item['signal'].connect( item['slot'] )  
    else:
      self.hasConnect = False
      for item in ss:
        item['signal'].disconnect( item['slot'] )

  @QtCore.pyqtSlot(QgsCore.QgsMapLayer)
  def setLayer(self, layer ):
    if not layer is None and layer.type() == QgsCore.QgsMapLayer.RasterLayer:
      self.layer = layer
      self.resX = layer.rasterUnitsPerPixelX() 
      self.resY = layer.rasterUnitsPerPixelY()
      self.setParamsImageView()
    else:
      self.layer = None

  @QtCore.pyqtSlot()
  def setParamsImageView(self):
    def getInitCoord( cMinLayer, cPoint, res ):
      return int( ( cPoint - cMinLayer ) / res ) * res + cMinLayer
    #
    def getEndCoord( cMaxLayer, cPoint, res ):
      return cMaxLayer - int( ( cMaxLayer - cPoint ) / res ) * res
    #
    self.paramsImgView = None

    if self.layer is None:
      self.msgError = "Current layer need be Raster type"
      self.iface.messageBar().pushMessage( self.titleMsg, self.msgError, QgsGui.QgsMessageBar.WARNING, 5 )
      return

    mapSettings = self.canvas.mapSettings()
    crsCanvas = mapSettings.destinationCrs()
    extentCanvas = self.canvas.extent()

    if self.layer.crs() != crsCanvas:
      extentCanvas = mapSettings.mapToLayerCoordinates( self.layer, extentCanvas )

    extentLayer = self.layer.extent()
    if not extentCanvas.intersects( extentLayer ):
      self.msgError = "View not intersects Raster '%s'" % self.layer.name()
      self.iface.messageBar().pushMessage( self.titleMsg, self.msgError, QgsGui.QgsMessageBar.WARNING, 5 )
      return

    if extentCanvas == extentLayer or extentCanvas.contains( extentLayer):
      self.msgError = "View has all raster '%s'" % self.layer.name()
      self.iface.messageBar().pushMessage( self.titleMsg, self.msgError, QgsGui.QgsMessageBar.WARNING, 5 )
      return

    extent = extentCanvas.intersect( extentLayer )
    #
    iniX = getInitCoord( self.layer.extent().xMinimum(), extent.xMinimum(), self.resX )
    iniY = getInitCoord( self.layer.extent().yMinimum(), extent.yMinimum(), self.resY )
    endX = getEndCoord ( self.layer.extent().xMaximum(), extent.xMaximum(), self.resX )
    endY = getEndCoord ( self.layer.extent().yMaximum(), extent.yMaximum(), self.resY )
    #
    extent.set( iniX,iniY, endX, endY  )
    widthRead  = int( extent.width()  / self.resX )
    heightRead = int( extent.height() / self.resY )
    #
    self.paramsImgView = { 'extent': extent, 'widthRead': widthRead, 'heightRead': heightRead }

  def setTypeBlockImage( self, isProvider=True ):
    self.isTypeBlockProvider = isProvider

  def setBlockImage(self):
    def setImageProviderRGB():
      bands = ( 1, 2, 3 )
      f = self.layer.dataProvider().block
      imgBands = map( lambda item: f( item, p_e, p_w, p_h ) , bands )
      #
      block = QgsCore.QgsRasterBlock( QgsCore.QGis.ARGB32, p_w, p_h, 0.0 )
      for row in range( p_h ):
        for col in range( p_w ):
          rgb = []
          for band in imgBands:
            rgb.append( band.value( row, col ) )
          block.setColor( row, col, QtGui.qRgb( rgb[0], rgb[1], rgb[2] ) )
      #
      self.blockImage = block.image()
      block.reset( QgsCore.QGis.ARGB32, p_w, p_h, 0.0 )
      del block
    #
    def setImageRenderRGB():
      rr = self.layer.renderer()
      self.blockImage = rr.block( 1, p_e, p_w, p_h ).image() # integer in format #AARRGGBB
    #
    if not self.blockImage is None:
      del self.blockImage
      self.blockImage = None
    #
    if self.paramsImgView is None:
      self.iface.messageBar().pushMessage( self.titleMsg, self.msgError, QgsGui.QgsMessageBar.WARNING, 5 )
      return
    #
    ( p_e, p_w, p_h ) = map( lambda item: self.paramsImgView[ item ], ( 'extent', 'widthRead', 'heightRead' ) )
    #
    if self.isTypeBlockProvider:
      typeImage = 'Provider'
      setImageProviderRGB()
    else:
      typeImage = 'Renderer'
      setImageRenderRGB()
    #
    if self.blockImage.isNull():
      msg = "Image(%s): width = %d, height = %d" % ( typeImage, p_w, p_h )
      self.msgError = "Block Invalid! %s" % msg
      self.iface.messageBar().pushMessage( self.titleMsg, self.msgError, QgsGui.QgsMessageBar.CRITICAL, 5 )
      del self.blockImage
      self.blockImage = None

  def saveBlockImage(self, fileName):
    def addGeoInfo():
      ds = gdal.Open( fileName, GA_Update )
      ds.SetProjection( str( self.layer.crs().toWkt() ) )
      p_e = self.paramsImgView[ 'extent' ]
      ds.SetGeoTransform( [ p_e.xMinimum(), self.resX, 0, p_e.yMaximum(), 0, -1*self.resY ] )
      del ds
      ds = None
    #
    self.setBlockImage()
    if self.blockImage is None:
      self.iface.messageBar().pushMessage( self.titleMsg, self.msgError, QgsGui.QgsMessageBar.WARNING, 5 )
      return
    #
    self.blockImage.save( fileName )
    addGeoInfo() # Adpatar para o Renderer (resolucao de tela)
  
  # Adaptation from https://github.com/hmeine/qimage2ndarray/blob/master/qimage2ndarray/qimageview_python.py
  def getBlockArrayNumpy(self):
    self.setBlockImage()
    if self.blockImage is None:
      self.iface.messageBar().pushMessage( self.titleMsg, self.msgError, QgsGui.QgsMessageBar.WARNING, 5 )
      return None
    #
    shape = self.blockImage.height(), self.blockImage.width()
    strides0 = self.blockImage.bytesPerLine()
    dtype, strides1 = "|u4", 4 # Use for 32bits image
    #
    self.blockImage.__array_interface__ = {
      'shape': shape,
      'typestr': dtype,
      'data': ( int( self.blockImage.bits() ), False ),
      'strides': ( strides0, strides1 ),
      'version': 3,
    }
    result = np.asarray( self.blockImage )
    del self.blockImage.__array_interface__
    #
    return result
  
  def rgbValues(self, arryNumpy, row, col):
    rgb = int( arryNumpy[ row, col ] )
    return "%d = R: %d, G: %d, B: %d" % ( rgb, QtGui.qRed( rgb ), QtGui.qGreen( rgb ), QtGui.qBlue( rgb ) )

print "------------ Usage --------------"
print "cbi = CurrentBlockImage(iface)"
print "------------ Save ---------------"
print "cbi.setTypeBlockImage( False ) # For change for Renderer, default Provider" 
print "fileName = '~/temp/test1.tif'"
print "cbi.saveBlockImage(fileName)"
print "------------ Numpy --------------"
print "arryNumpy = cbi.getBlockArrayNumpy()"
print "cbi.rgbValues( arryNumpy, row=0, col=0 )"
print "------------ Clear --------------"
print "del cbi"
print "del arryNumpy"
print "---------------------------------"
