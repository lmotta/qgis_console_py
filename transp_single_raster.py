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
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from qgis.core  import QgsRasterTransparency

class ToggleLegendRaster(QObject):
  def __init__(self, layer, tvLegend):
    def initLegendToggle():
      legendColorAll = layer.legendSymbologyItems()
      self.legendAll = map( lambda x: x[0], legendColorAll )
      self.legendToggle = dict( ( x, True ) for x in self.legendAll )

    super(ToggleLegendRaster, self).__init__() # QThread
    #
    self.layer = layer
    self.tvLegend = tvLegend
    self.transparency = layer.renderer().rasterTransparency()
    self.legendToggle = self.legendAll = None
    initLegendToggle()
    #
    self.tvLegend.activated.connect( self.toggle )
   
  def __del__(self):
    self.tvLegend.activated.disconnect( self.toggle )

  def refreshLayer(self):
    if  hasattr( layer, "setCacheImage" ):
      layer.setCacheImage(None) # Refresh
    else:
      layer.triggerRepaint()

  @pyqtSlot('QModelIndex')
  def toggle(self, index ):
    def setShow(legend, show):
      value = self.legendAll.index( legend )
      t = QgsRasterTransparency.TransparentSingleValuePixel()
      t.min = t.max = value
      t.percentTransparent = 100.0 if not show else 0.0

      return t
    
    layer = self.layer.name()
    parent = index.parent().data()
    data = index.data()
    if data == layer:
      self.showAll()
      return
    elif not parent == layer:
      return

    self.legendToggle[ data ] = not self.legendToggle[ data ]
    values = map( lambda x: setShow( x, self.legendToggle[ x ] ), self.legendToggle.keys() )
    self.transparency.setTransparentSingleValuePixelList( values )
    self.refreshLayer()
    del values[:]

  @pyqtSlot()
  def showAll(self):
    self.transparency.setTransparentSingleValuePixelList([])
    self.refreshLayer()
    #
    for item in self.legendToggle.keys():
      self.legendToggle[ item ] = True

# Main
layer = iface.activeLayer()
tvLegend = qgis.utils.iface.layerTreeView()
#
if layer is None:
  print "Select layer"
else:
  t = ToggleLegendRaster( layer, tvLegend )

# del t
