from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt4.QtGui import QMessageBox

from qgis.core import QgsMapLayerRegistry
from qgis.gui  import ( QgsMessageBar )

class WorkerSensitiveLegendRaster(QObject):

  # Signals 
  finished = pyqtSignal()
  messageResult = pyqtSignal( str )
  messageStatus = pyqtSignal( str )

  def __init__(self):
    super(WorkerSensitiveLegendRaster, self).__init__()
    self.isKilled = None
    self.readBlock = self.extent = self.widthRead = self.heightRead = None
    self.legendAll = None

  def setLegendReadBlock(self, layer):
    self.readBlock = layer.dataProvider().block
    legendColorAll = layer.legendSymbologyItems() #Future
    self.legendAll = map( lambda x: x[0], legendColorAll )

  def setProcessImage(self, extent, widthRead, heightRead):
    ( self.extent, self.widthRead, self.heightRead ) = ( extent, widthRead, heightRead )
    self.isKilled = False

  @pyqtSlot()
  def run(self):
    def sendResult():
      keys = filter( lambda x: pixels_values[x] > 0, pixels_values )
      pixels_values.clear()
      #
      values = sorted( map( lambda x: int(x), keys ) )
      del keys[:]
      #
      legendsView = map( lambda x: "(%s)%s" % ( x, self.legendAll[int(x)] ), values )
      del values[:]
      #
      msg = "[%d] = %s" % ( len( legendsView ), ' '.join( legendsView ) )
      del legendsView[:]
      #
      self.messageResult.emit( msg )

    self.messageStatus.emit( "Reading image..." )

    keysLegend = range( len(self.legendAll) )
    # pixels_values = { float'idClass': ZERO ...} *** block.value return 'float'
    pixels_values = dict( ( float(x),0 ) for x in keysLegend )
    del keysLegend[:]
    data = self.readBlock(  1, self.extent, self.widthRead, self.heightRead )
    h = 0
    stepStatus = 10.0
    showStatus = stepStatus
    value = 0.0
    while h < self.heightRead:
      w = 0
      #
      if self.isKilled:
        pixels_values.clear()
        del data
        self.finished.emit()
        return
      #
      perc = 100.0 * float(h+1) / self.heightRead
      if perc >= showStatus:
        msg = "Calculating legend... %d %%" % int(perc)
        self.messageStatus.emit( msg )
        showStatus += stepStatus
      #
      while w < self.widthRead:
        pixels_values[ data.value(h,w) ] += 1
        w += 1
      h += 1
    del data
    
    sendResult() # Clean pixels_values

    self.finished.emit()

class SensitiveLegendRaster(QObject):
  def __init__(self):
    super(SensitiveLegendRaster, self).__init__() # QThread
    self.layer = self.worker = self.thread = None
    self.canvas = iface.mapCanvas()
    self.msgBar = iface.messageBar()
    self.legend = iface.legendInterface()
    self.nameModulus = "Script_Sensitive_Legend"
    #
    self.initThread()
    self._connect()
    #
    self.selectLayer( iface.activeLayer() )

  def __del__(self):
    self.finishThread()
    self._connect( False )

  def printMsgBar(self, msg, typeMsg=QgsMessageBar.INFO):
    self.msgBar.popWidget()
    if typeMsg == QgsMessageBar.INFO:
      self.msgBar.pushMessage( 'SensitiveLegendRaster Script', msg, typeMsg )
    else:
      self.msgBar.pushMessage( 'SensitiveLegendRaster Script', msg, typeMsg, 5 )

  def initThread(self):
    self.thread = QThread( self )
    self.thread.setObjectName( self.nameModulus )
    self.worker = WorkerSensitiveLegendRaster()
    self.worker.moveToThread( self.thread )
    self._connectWorker()

  def finishThread(self):
    self._connectWorker( False )
    self.worker.deleteLater()
    self.thread.wait()
    self.thread.deleteLater()
    self.thread = self.worker = None

  def _connectWorker(self, isConnect = True):
    ss = [
      { 'signal': self.thread.started, 'slot': self.worker.run },
      { 'signal': self.worker.finished, 'slot': self.finishedWorker },
      { 'signal': self.worker.messageResult, 'slot': self.messageResultWorker },
      { 'signal': self.worker.messageStatus, 'slot': self.messageStatusWorker }
    ]
    if isConnect:
      for item in ss:
        item['signal'].connect( item['slot'] )  
    else:
      for item in ss:
        item['signal'].disconnect( item['slot'] )

  def _connect(self, isConnect = True):
    ss = [
      { 'signal': self.legend.currentLayerChanged, 'slot': self.selectLayer },
      { 'signal': QgsMapLayerRegistry.instance().layerWillBeRemoved, 'slot': self.unselectLayer },
      { 'signal': self.canvas.extentsChanged, 'slot': self.changeSensitiveLegend }
    ]
    if isConnect:
      for item in ss:
        item['signal'].connect( item['slot'] )  
    else:
      for item in ss:
        item['signal'].disconnect( item['slot'] )

  @pyqtSlot()
  def finishedWorker(self):
    self.thread.quit()
    if self.worker.isKilled: # When PAN/ZOOM/...
      self.thread.wait()
      self.changeSensitiveLegend()

  @pyqtSlot( str )
  def messageResultWorker(self, msg):
    self.printMsgBar( msg )

  @pyqtSlot( str )
  def messageStatusWorker(self, msg):
    self.printMsgBar( msg )

  @pyqtSlot( 'QgsMapLayer' )
  def selectLayer(self, layer):

    if self.thread.isRunning():
      return

    isOk = True
    msg = ''
    typeMsg = QgsMessageBar.WARNING
    if not layer is None and layer.type() ==  QgsMapLayer.RasterLayer:
      legendColorAll = layer.legendSymbologyItems()
      if len( legendColorAll ) > 0: # Had a classification
        self.layer = layer
        self.worker.setLegendReadBlock( layer )
        msg = "Raster Layer '%s' actived" % layer.name()
        typeMsg = QgsMessageBar.INFO
      else:
        msg = "Raster Layer '%s' need be a classification" % layer.name()
        isOk = False
    else:
      if layer is None:
        msg = "Active a Raster layer"
      else:
        msg = "Layer '%s' need be a Raster" % layer.name()
      isOk = False

    self.printMsgBar( msg, typeMsg )

    return isOk

  @pyqtSlot( str )
  def unselectLayer(self, idLayer):
    if idLayer == self.layer.id():
      if self.thread.isRunning():
        self.worker.isKilled = True
      msg = "Raster Layer '%s' was removed" % self.layer.name()
      self.printMsgBar( msg, QgsMessageBar.WARNING )
      self.layer = None

  @pyqtSlot()
  def changeSensitiveLegend(self):

    if self.layer is None:
      return

    if self.thread.isRunning():
      self.worker.isKilled = True
      return

    mapSettings = self.canvas.mapSettings()
    crsCanvas = mapSettings.destinationCrs()
    extentCanvas = self.canvas.extent()
    
    extentLayer = self.layer.extent()
    resX = self.layer.rasterUnitsPerPixelX() 
    resY = self.layer.rasterUnitsPerPixelY()
    
    if self.layer.crs() != crsCanvas:
      extentCanvas = mapSettings.mapToLayerCoordinates( self.layer, extentCanvas )

    if not extentCanvas.intersects( extentLayer ):
      self.printMsgBar( "View not intersects Raster '%s'" % self.layer.name, QgsMessageBar.WARNING )
      return
    
    keysLegend = range( len(self.worker.legendAll) ) # [ idClass1, idClass2, ... ] [ 0..N-1]

    if extentCanvas == extentLayer or extentCanvas.contains( extentLayer):
      legendsView = map( lambda x: "(%s)%s" % ( x, self.worker.legendAll[x] ), keysLegend )
      msg = "[%d] = %s" % ( len( legendsView ), ' '.join( legendsView ) )
      self.printMsgBar( msg )
      return

    extent = extentCanvas.intersect( extentLayer )
    widthRead  = int( extent.width()  / resX ) + 1
    heightRead = int( extent.height() / resY ) + 1

    self.worker.setProcessImage( extent, widthRead, heightRead )
    self.thread.start()
    #self.worker.run() # DEBUG

t = SensitiveLegendRaster()
# del t
