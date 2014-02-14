import os.path
import os

def getAssetsPath():
  ap =  os.path.join(os.path.expanduser("~"),"erfgoedstats")
  if not os.path.exists(ap):
    os.makedirs(ap)
  return ap

def getAssetsPathFor(fn):
  fn = fn.lstrip(os.sep)
  return os.path.join(getAssetsPath(),fn)


def getBaseNameFor(fn):
  fn = fn.rstrip(os.sep)
  return os.path.basename(fn)
  