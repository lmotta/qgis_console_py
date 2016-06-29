import math

def azimuth(p1, p2):
  dx = p2.x() - p1.x()
  dy = p2.y() - p1.y()
  az = math.atan2( dx, dy ) * 180.0 / math.pi
  if az < 0.0:
    az = 360.0 - abs( az )
  return az

def changePolygonWithToleranceAzimuth(polygon, threshold):
  hasChange = False
  for id in xrange( len( polygon ) ):
    points = polygon[ id ]
    if len( points ) < 4:
      continue
    ids_new = [ 0 ]
    for i in xrange( 1, len( points ) -1 ):
      aznew = azimuth( points[ ids_new[-1] ], points[ i ] )
      az = azimuth( points[ i ], points[ i+1 ] )
      if abs( az - aznew ) > threshold:
        ids_new.append( i )
    if len( ids_new ) < len( points ):
      hasChange = True
      ids_remove = list( set( range( len( points ) ) ) - set( ids_new ) )
      ids_remove.sort()
      ids_remove.reverse()
      for i in xrange( len( ids_remove ) ):
        del polygon[ id ][ ids_remove[ i ] ]

  return hasChange

def showAzimuth():
  layer = iface.activeLayer()
  feats = layer.selectedFeatures()
  geom = feats[0].geometry()
  isMulti = True
  polygon = geom.asMultiPolygon()
  if len( polygon) == 0:
    polygon = geom.asPolygon()
    isMulti = False
  if isMulti:
    return

  # Single poly - Outer ring
  points = polygon[0]
  for i in xrange( len( points ) -1 ):
    az = azimuth( points[i], points[i+1] )
    print " %d-%d) Azimuth: %f" % ( i, i+1, az )
 
def changeGeomWithToleranceAzimuth(layer, threshold):
  def getGeomTolerance(geom, fc):
    vreturn = None
    hasChange = False
    if geom.isMultipart():
      mp = geom.asMultiPolygon()
      for id in xrange( len( mp) ):
        if fc( mp[ id ], threshold ):
          hasChange = True
      vreturn = { 'hasChange': hasChange }
      if hasChange:
        vreturn['geom'] = QgsGeometry.fromMultiPolygon( mp )
    else:
      p = geom.asPolygon()
      hasChange = fc( p, threshold )
      vreturn = { 'hasChange': hasChange }
      if hasChange:
        vreturn['geom'] = QgsGeometry.fromPolygon( p )

    return vreturn

  isEditable = layer.isEditable()
  if not isEditable:
    layer.startEditing()
  inter = layer.getFeatures()
  id = 0
  for feat in inter:
    geom = feat.geometry()
    vreturn = getGeomTolerance( geom, changePolygonWithToleranceAzimuth )
    if vreturn['hasChange']:
      layer.changeGeometry( id, vreturn['geom'] )
    id += 1
  layer.commitChanges()
  if isEditable:
    layer.startEditing()
 
#showAzimuth()
#changeGeomWithToleranceAzimuth( iface.activeLayer(), 5)

