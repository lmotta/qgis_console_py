# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Legend Coordinate Reference Systems
Description          : Show in TreeView CRS of layers
Date                 : March, 2016
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

from PyQt4.QtCore import QObject, pyqtSlot, Qt
from PyQt4.QtGui import QDockWidget, QTreeView, QStandardItemModel, QStandardItem

from qgis.core import QgsMapLayer, QgsMapLayerRegistry


class TreeLegendCRS(QObject):

  def __init__(self, iface):
    super(TreeLegendCRS, self).__init__()
    self.iface = iface
    self.model = QStandardItemModel( 0, 1 )
    #
    self.tree = QTreeView( None )
    self.tree.setAttribute(Qt.WA_DeleteOnClose)
    self.tree.setModel( self.model )
    self.tree.setSelectionMode( 0 ) # no selection
    self.tree.setHeaderHidden( True )
    #
    self.dock = QDockWidget( "CRS of Layers", iface.mainWindow() )
    self.dock.setWidget( self.tree )
    #
    self._connect()

  def __del__(self):
    self.model.clear()
    self._connect( False )

  def _connect(self, isConnect = True):
    ss = [
      { 'signal': self.tree.clicked, 'slot': self.setCurrentLayer },
      { 'signal': QgsMapLayerRegistry.instance().legendLayersAdded, 'slot': self.updateLegend },
      { 'signal': QgsMapLayerRegistry.instance().layersRemoved, 'slot': self.updateLegend }
    ]
    if isConnect:
      self.hasConnect = True
      for item in ss:
        item['signal'].connect( item['slot'] )  
    else:
      self.hasConnect = False
      for item in ss:
        item['signal'].disconnect( item['slot'] )

  def addLegend(self):
    self.updateLegend()
    self.iface.addDockWidget( Qt.LeftDockWidgetArea , self.dock )

  @pyqtSlot(list)
  def updateLegend(self, lst=None):
    def getCrs_Layers():
      layers = self.iface.legendInterface().layers()
      crs_layers = {}
      for layer in layers:
        crs = layer.crs().authid()
        if not crs_layers.has_key( crs):
          crs_layers[ crs ] = [ layer ]
        else:
          crs_layers[ crs ].append( layer )

      return crs_layers

    def createItem( data ):
      item = None
      if isinstance( data, QgsMapLayer):
        item = QStandardItem( data.name() )
        item.setData( data, Qt.UserRole )
      else:
        item = QStandardItem( data )
      item.setEditable( False )

      return item

    self.model.clear()
    for crs, layers in getCrs_Layers().iteritems():
      name = "%s (%d)" % ( crs, len( layers ) )
      itemCRS = createItem( name )
      self.model.appendRow( itemCRS ) 
      for layer in layers:
        itemLayer = createItem( layer )
        itemCRS.appendRow( itemLayer )

  @pyqtSlot('QModelIndex')
  def setCurrentLayer(self, index):
    data = index.data( Qt.UserRole )
    if not data is None:
      self.iface.setActiveLayer( data )

def initTreeLegendCRS():
  tl = TreeLegendCRS( iface )
  tl.addLegend()
  return tl

try:
  if not tl.dock.isVisible():
    tl.dock.show()
except NameError:
  tl = initTreeLegendCRS()
