from osgeo import ogr
from random import randint, random
import sys

inputds = sys.argv[1]

driver = ogr.GetDriverByName("ESRI Shapefile")
ds = driver.Open(inputds, True)
layer = ds.GetLayer(0)
numFeatures = layer.GetFeatureCount()
for i in range(numFeatures):
    feature = layer.GetFeature(i)
    feature.SetField('Int_Attrib',randint(0,9999))
    feature.SetField('Float_Attr', random())
    layer.SetFeature(feature)
    feature.Destroy()
