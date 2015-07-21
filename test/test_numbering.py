#-------------------------------------------------------------------------------
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import sys, os
sys.path.append("C:\Users\iacopo.borsi\.qgis2\python\plugins\Freewat")

from qgridder_utils import get_rgrid_nrow_ncol
gridLayer = iface.mapCanvas().currentLayer()

#gridLayer.startEditing()

###
##a = [1.5,1.5,1.5,3.0,3.0,3.0]
##b = [2.0,4.0,6.0,2.0,4.0,6.0]
##c = [-1*b[i] for i in range(len(b))]
##ind = np.lexsort((a,c))
##[(a[i], -c[i]) for i in ind]
##[(1.5, 6.0), (3.0, 6.0), (1.5, 4.0), (3.0, 4.0), (1.5, 2.0), (3.0, 2.0)]


allFeatures = {feat.id():feat for feat in gridLayer.getFeatures()}
allCentroids = [feat.geometry().centroid().asPoint() for feat in allFeatures.values()]
centroids_ids = allFeatures.keys()

centroids_x = np.around(np.array([centroid.x() for centroid in allCentroids]), 2)
centroids_y = np.around(np.array([centroid.y() for centroid in allCentroids]), 2)
centroids = np.array( [centroids_ids , centroids_x, centroids_y] )
centroids = centroids.T

# Iterate over grid row-wise and column wise
# sort by decreasing y and increasing x
idx = np.lexsort( [centroids_x,-1*centroids_y] )
centroids = centroids[idx,:]


row_field_idx = gridLayer.dataProvider().fieldNameIndex('ROW')
col_field_idx = gridLayer.dataProvider().fieldNameIndex('COL')

if row_field_idx == -1:
   # if caps & QgsVectorDataProvider.AddAttributes:
    res = gridLayer.dataProvider().addAttributes(  [QgsField("ROW", QVariant.Int)] )
    row_field_idx = gridLayer.dataProvider().fieldNameIndex('ROW')
if col_field_idx == -1:
    #if caps & QgsVectorDataProvider.AddAttributes:
    res = res*gridLayer.dataProvider().addAttributes( [QgsField("COL", QVariant.Int)] )
    col_field_idx = gridLayer.dataProvider().fieldNameIndex('COL')

# update fields
gridLayer.updateFields()

# get nrow, ncol
nrow, ncol =  get_rgrid_nrow_ncol(gridLayer)
#nrow, ncol =  15 , 10

# start editing
gridLayer.startEditing()

row = 1
col = 1
print centroids.shape[0]

for i in range(centroids.shape[0]):
    if col > ncol:
	    col = 1
	    row = row + 1

    featId = centroids[i, 0]
##    print featId, 'col = ', col, 'row = ', row
##    print 'campo id = ', row_field_idx, col_field_idx

    gridLayer.changeAttributeValue(featId, row_field_idx, row)
    gridLayer.changeAttributeValue(featId, col_field_idx, col)
    col = col + 1

    # commit
gridLayer.commitChanges()

