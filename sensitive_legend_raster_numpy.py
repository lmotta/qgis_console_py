# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Raster legend sensitive
Description          : Testing sensitive legend.
Date                 : February, 2016
copyright            : (C) 2016 by Luiz Motta
email                : motta.luiz@gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# t = SensitiveLegendRaster()
# t.selectLayer()

from osgeo import gdal
import numpy
from qgis.gui  import ( QgsMessageBar )

class SensitiveLegendRaster():
  def __init__(self):
    self.ds = None
    self.canvas = iface.mapCanvas()
    self.msgBar = iface.messageBar()

  def __del__(self):
    if not self.ds is None:
      self.canvas.extentsChanged.disconnect( self.changeLegend )
      self.ds = None
      self.msgBar.popWidget()

  def printMsgBar(self, msg, typeMsg=QgsMessageBar.INFO):
    self.msgBar.popWidget()
    if typeMsg == QgsMessageBar.INFO:
      self.msgBar.pushMessage( 'SensitiveLegendRaster Script', msg, typeMsg )
    else:
      self.msgBar.pushMessage( 'SensitiveLegendRaster Script', msg, typeMsg, 5 )


  def selectLayer(self):
    def setDataset():
      self.ds = gdal.Open( layer.source() )
      self.name = layer.name()
      #
      self.legendAll = map( lambda x: x[0], layer.legendSymbologyItems() )
      #
      self.crsLayer = layer.crs()
      self.extentLayer = layer.extent()
      self.unitXLayer = layer.rasterUnitsPerPixelX ()
      self.unitYLayer = layer.rasterUnitsPerPixelY ()
      #
      self.canvas.extentsChanged.connect( self.changeLegend )

    # Clean
    if not self.ds is None:
      self.ds = None
      self.canvas.extentsChanged.disconnect( self.changeLegend )
      
    layer = iface.activeLayer()
    msg = ''
    typeMsg = QgsMessageBar.WARNING
    if not layer is None and layer.type() ==  QgsMapLayer.RasterLayer:
      legendColorAll = layer.legendSymbologyItems()
      if len( legendColorAll ) > 0: # Had a classification
        self.legendColorAll = legendColorAll
        setDataset()
        msg = "Raster Layer '%s' actived" % layer.name()
        typeMsg = QgsMessageBar.INFO
      else:
        msg = "Raster Layer '%s' need be a classification" % layer.name()
    else:
      if layer is None:
        msg = "Active a Raster layer"
      else:
        msg = "Layer '%s' need be a Raster" % layer.name()

    self.printMsgBar( msg, typeMsg )

  def changeLegend(self):
    mapSettings = self.canvas.mapSettings()
    crsCanvas = mapSettings.destinationCrs()
    extentCanvas = self.canvas.extent()
    
    if self.crsLayer != crsCanvas:
      extentCanvas = mapSettings.mapToLayerCoordinates( self.layer, extentCanvas )

    if not extentCanvas.intersects( self.extentLayer ):
      self.printMsgBar( "View not intersects Raster '%s'" % self.name, QgsMessageBar.WARNING )
      return
    
    if extentCanvas.contains( self.extentLayer ) or extentCanvas == self.extentLayer:
      self.printMsgBar( "[%d] = All legends" % len( self.legendAll ) )
      return

    extent = extentCanvas.intersect( self.extentLayer )
    # Origin subset
    xoff = int( ( extent.xMinimum() - self.extentLayer.xMinimum() ) / self.unitXLayer )
    yoff = int( ( extent.yMinimum() - self.extentLayer.yMinimum() ) / self.unitYLayer )
    # Lenght subset
    xcount = int( round( extent.width()  / self.unitXLayer ) )
    ycount = int( round( extent.height() / self.unitYLayer ) )

    band = self.ds.GetRasterBand(1)
    dataRaster = band.ReadAsArray( xoff, yoff, xcount, ycount )
    values = numpy.unique( dataRaster )
    legendsView = map( lambda x: "(%s)%s" % ( x, self.legendAll[int(x)] ), values )
    msg = "[%d] = %s" % ( len( legendsView ), ' '.join( legendsView ) )
    
    msgDebug = ""
    
    self.printMsgBar( msg )
  
