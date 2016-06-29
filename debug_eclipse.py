import sys

eclipse_path = '/home/lmotta/.eclipse/org.eclipse.platform_4.6.0_1473617060_linux_gtk_x86_64'
pydev_path = "%s/%s" % ( eclipse_path, '/plugins/org.python.pydev_5.1.1.201606162013/pysrc' )
sys.path.append(pydev_path)
started = False
try:
  import pydevd
  pydevd.settrace(port=5678, suspend=False)
  started = True
except:
  pass

print "Debug active" if started else "Debug not active! Run Eclipse DEBUG server"
