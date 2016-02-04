from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from qgis.core  import QgsRasterTransparency

class ToggleLegendRaster(QObject):
  def __init__(self, layer, tvLegend):
    def initLegendToggle():
      legendColorAll = layer.legendSymbologyItems()
      legendAll = map( lambda x: x[0], legendColorAll )
      keysLegend = range( len(legendAll) )
      self.legendToggle = dict( ( x, True ) for x in keysLegend )

    super(ToggleLegendRaster, self).__init__() # QThread
    #
    self.layer = layer
    self.tvLegend = tvLegend
    self.transparency = layer.renderer().rasterTransparency()
    self.legendToggle = {}
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

  def setAllVisible(self):
    for item in self.legendToggle.keys():
      self.legendToggle[ item ] = True

  @pyqtSlot('QModelIndex')
  def toggle(self, index ):
    def setShow(id, show):
      t = QgsRasterTransparency.TransparentSingleValuePixel()
      t.min = t.max = id
      t.percentTransparent = 100.0 if not show else 0.0

      return t
    
    if not index.parent().data() == self.layer.name():
      self.showAll()
      return

    id = index.row()

    self.legendToggle[id] = not self.legendToggle[id]
    values = map( lambda x: setShow( x, self.legendToggle[ x ] ), self.legendToggle.keys() )
    self.transparency.setTransparentSingleValuePixelList( values )
    self.refreshLayer()
    del values[:]

  @pyqtSlot()
  def showAll(self):
    self.transparency.setTransparentSingleValuePixelList([])
    self.refreshLayer()
    self.setAllVisible()

# Main
layer = iface.activeLayer()
tvLegend = qgis.utils.iface.layerTreeView()
#
if layer is None:
  print "Select layer"
t = ToggleLegendRaster( layer, tvLegend )
# del t
