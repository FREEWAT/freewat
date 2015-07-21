__author__ = 'xander'

import os
import sys

sys.path.append("C:\Users\iacopo.borsi\.qgis2\python\plugins\Freewat")
from mdoCreate_utils import createRiverLayer


##def testRiverToFields(riverName, gridName):
##
##    rh_in = 20.0
##    rh_out = 26.0
##    bt_in = 20.0
##    bt_out = 26.0
##    krb_in = 0.01
##    krb_out = 0.01
##    th_in = 1.0
##    th_out = 2.0
##    riverToFields.riverToFields(riverName, gridName, rh_in, rh_out, bt_in,
##                                bt_out, krb_in, krb_out, th_in, th_out)



riverName = 'fiume_digit'
gridName = 'griglia_test'
csvName = 'csv_per_river'


riverLayer = QgsMapLayerRegistry.instance().mapLayersByName(riverName)[0]
csvlayer = QgsMapLayerRegistry.instance().mapLayersByName(csvName)[0]
gridLayer = QgsMapLayerRegistry.instance().mapLayersByName(gridName)[0]

width = 3.0
nsp = 2
dbName = 'C:/Users/iacopo.borsi/Desktop/ale.sqlite'
layer = 1
xyz = 2


createRiverLayer('px', dbName, gridLayer, riverLayer, csvlayer, width, layer, xyz, nsp )