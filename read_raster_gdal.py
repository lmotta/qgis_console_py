# http://geoinformaticstutorial.blogspot.com.br/2012/09/reading-raster-data-with-python-and-gdal.html
# https://docs.python.org/2/library/struct.html

from osgeo import ( gdal, ogr, osr )
from gdalconst import ( GA_ReadOnly, GA_Update )

import struct

ds = gdal.Open(band = ds.GetRasterBand( 1 )
band = ds.GetRasterBand( 1 )

# B: unsigned char = Byte
print gdal.GetDataTypeName(band.DataType)


# scanline = band.ReadRaster( xoff, yoff, xsize, ysize, buf_xsize = None, buf_ysize = None, buf_type = None, band_list = None )


# Scan First Line - Horizontal
xoff = 0
yoff = 0
xsize = band.XSize
ysize = 1
scanline = band.ReadRaster( xoff, yoff, xsize, ysize )
value = struct.unpack('B' * xsize * ysize, scanline)
#
del scanline
del value
# Scan Last Column Line - Vertical
xoff = band.XSize - 1
yoff = 0
xsize = 1
ysize = band.YSize
scanline = band.ReadRaster( xoff, yoff, xsize, ysize )
value = struct.unpack('B' * xsize * ysize, scanline)
#
del scanline
del value
# Midle Column
xoff = (band.XSize/2)
yoff = 0
xsize = 1
ysize = band.YSize
scanline = band.ReadRaster( xoff, yoff, xsize, ysize )
value = struct.unpack('B' * xsize * ysize, scanline)
