import os, re

def getDirPluginGimp():
  # ~/.gimp-2.8/plug-ins/  ~/Library/GIMP/2.8/  ~/Library/Application Support/GIMP/2.8/
  l_dirPlugin = []
  mask = r".*gimp.[0-9]+\.[0-9]+%s%s" % ( os.sep, nameDirPlugin )
  for root, dirs, files in os.walk( dirHome ):
    if re.match( mask, root, re.IGNORECASE):
      l_dirPlugin.append( root )
  return l_dirPlugin[0] if l_dirPlugin > 0 else None


dirHome = os.path.expanduser('~')
nameDirPlugin = "plug-ins"
dirPluginGimp = getDirPluginGimp()
msg = "Diretory of GIMP Plugins: %s" % dirPluginGimp
if dirPluginGimp is None:
  msg = "Not found diretory 'GIMP' or 'GIMP %s' in '%s'" % ( nameDirPlugin, dirHome )
print msg
