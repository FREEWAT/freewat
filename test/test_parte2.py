#-------------------------------------------------------------------------------
# Name:        modulo1
# Purpose:
#
# Author:      iacopo.borsi
#
# Created:     26/02/2015
# Copyright:   (c) iacopo.borsi 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#  --- ora crea un mode layer
# NOTE : AT THIS STEP, THE GRID LAYER MUST
# BE SELECTED IN THE QGIS LAYER LIST PANEL
gridLayer = qgis.utils.iface.activeLayer()




# Load model layers:
nomelayer1 =  'aquifer2'
##
top = 20.0
bottom = 0.0

# Values for LPF table
layType     = 'convertible'
layAverage  = 'harmonic'
chani   = 1.0
layWet  = 'off'

# Define values of new feature for LPF
# --
ft = [nomelayer1, 1,2,3,4]
# --
if layType == 'convertible':
    ft[1] = 1
else:
    ft[1] = 0
# --
if layAverage == 'harmonic':
    ft[2] = 0
elif layAverage == 'logarithmic':
    ft[2] = 1
else:
    ft[2] = 2
# --
ft[3] = chani
# --
if layWet == 'off':
    ft[4] = 0
else:
    ft[4] = 1
# --
parameters = ft
##parameters2 = []
##parameters2.append(nomelayer2)
##for j in range(1,len(ft)):
##    parameters2.append(ft[j])

# Create a Model Layer
dbName = workingDir

createModelLayer(gridLayer, dbName, modelname, nomelayer1, parameters)
