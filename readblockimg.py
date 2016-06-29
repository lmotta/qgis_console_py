#
#rr.bandCount() = 1
#rr.usesBands() = [1, 2, 3]
#rr.dataType(1) = QGis.ARGB32_Premultiplied
#rr.type()
#rr.block(1, ) # int bandNo, const QgsRectangle &extent, int width, int height) override=0
#
# block.dataType() = QGis.ARGB32_Premultiplied
#block.height() = 190
#block.width () = 453
#
#
#image.byteCount()
#image.bits()
#image.save("/home/lmotta/data/work/teste_block_2.tif")
#
#
def getParamsBlockCurrentView(canvas, layer ):
  mapSettings = canvas.mapSettings()
  crsCanvas = mapSettings.destinationCrs()
  extentCanvas = canvas.extent()

  extentLayer = layer.extent()
  resX = layer.rasterUnitsPerPixelX() 
  resY = layer.rasterUnitsPerPixelY()

  if layer.crs() != crsCanvas:
    extentCanvas = mapSettings.mapToLayerCoordinates( layer, extentCanvas )

  if not extentCanvas.intersects( extentLayer ):
    msg = "View not intersects Raster '%s'" % layer.name()
    return { 'isOk': False, 'msg': msg }

  if extentCanvas == extentLayer or extentCanvas.contains( extentLayer):
    msg = "View has all  raster '%s'" % layer.name()
    return { 'isOk': False, 'msg': msg }

  extent = extentCanvas.intersect( extentLayer )
  widthRead  = int( extent.width()  / resX )
  heightRead = int( extent.height() / resY )
  #
  return { 'isOk': True, 'extent': extent, 'widthRead': widthRead, 'heightRead': heightRead }

# Adaptation from https://github.com/hmeine/qimage2ndarray/blob/master/qimage2ndarray/qimageview_python.py
def getArrayNumpy(image):
  shape = image.height(), imagergb.width()
  strides0 = image.bytesPerLine()
  dtype, strides1 = "|u4", 4 # Use for 32bits image
  #
  image.__array_interface__ = {
    'shape': shape,
    'typestr': dtype,
    'data': ( int( image.bits() ), False ),
    'strides': ( strides0, strides1 ),
    'version': 3,
  }
  import numpy as np
  result = np.asarray( image )
  del image.__array_interface__
  #
  return result

canvas = iface.mapCanvas()
layer = iface.activeLayer()
block = None
if layer is None or not layer.type() == QgsMapLayer.RasterLayer:
  iface.messageBar().pushMessage( "Warning", "Current layer is Raster type", QgsMessageBar.WARNING, 5)
else:
  data = getParamsBlockCurrentView( canvas, layer )
  if not data['isOk']:
    iface.messageBar().pushMessage( "Warning get Params for image", data['msg'], QgsMessageBar.WARNING, 5)
  else:def
    rr = layer.renderer()
    image = rr.block( 1, data['extent'], data['widthRead'], data['heightRead'] ).image()
    #
    block_p = layer.dataProvider().block( 1, data['extent'], data['widthRead'], data['heightRead'] )
    print block_p.value(0,0) # Red value (banda 1)
    #
    arr = getArrayNumpy( image )
    rgb = image.pixel( 0,0)
    print qRed( rgb ), qGreen( rgb ), qBlue( rgb )

