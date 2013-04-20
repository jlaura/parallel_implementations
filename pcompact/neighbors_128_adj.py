import pysal
from osgeo import ogr

w = pysal.rook_from_shapefile("20x20.shp")
infile = ogr.Open("20x20.shp", 1)
inlyr = infile.GetLayerByIndex(0)
counter = 0
feat = inlyr.GetNextFeature()
while feat is not None:
    feat.SetField('Adjacent', str(w.neighbors[counter]).split("[")[1].split("]")[0])
    counter += 1
    inlyr.SetFeature(feat)
    feat = inlyr.GetNextFeature()
