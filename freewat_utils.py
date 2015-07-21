# Crea nuovo layer come copia del layer attivo, ma shape file diverso

from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QVariant
from qgis.core import *
import ftools_utils as ft
import processing
import locale
import math
from osgeo import ogr, gdal
#import osr
import numpy
import sys, os


# Initialize Qt resources from file resources.py

# Utility: get a vector layer by name
# mutuated by plugin ftools:
def getVectorLayerNames():
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    layerNames = []
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.VectorLayer:
            layerNames.append(str(layer.name()))
    return layerNames


def getVectorLayerByName(layerName):
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.VectorLayer and layer.name() == layerName:
            if layer.isValid():
                return layer
            else:
                return None


##def getFieldNames(layer, fieldTypes):
##	fields = layer.pendingFields()
##	fieldNames = []
##	for field in fields:
##		if field.type() in fieldTypes and not field.name() in fieldNames:
##			fieldNames.append(unicode(field.name()))
##	return sorted(fieldNames, cmp=locale.strcoll)

def getFieldNames(layer ):
    fields = layer.pendingFields()
    fieldNames = []
    for field in fields:
        if not field.name() in fieldNames:
            fieldNames.append(unicode(field.name()))
    return sorted(fieldNames, cmp=locale.strcoll)

def getFieldType(layer, fieldName):
    fields = layer.pendingFields()
    for field in fields:
        if field.name() == fieldName:
            return field.typeName()


def getUniqueValuesCount(layer, fieldIndex, useSelection):
    count = 0
    values = []
    if useSelection:
        for f in layer.selectedFeatures():
            if f[fieldIndex] not in values:
                values.append(f[fieldIndex])
                count += 1
    else:
        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)
        for f in layer.getFeatures(request):
            if f[fieldIndex] not in values:
                values.append(f[fieldIndex])
                count += 1
    return count

# ---------------------------
def SelectByRegionAndSave_PointOnPolygon(inPoly, inPts):
        # INPUT:
        # inPoly: Multipolygon Layer where you want perform a selection
        # inPts:  Multipoint that intersects the polygon layer
        # OUTPUT:
        # newlayer: the vector layer (multipolygon) where the selection is saved (temporary file)
        inputLayer = ft.getVectorLayerByName(inPoly)
        selectLayer = ft.getVectorLayerByName(inPts)
        inputProvider = inputLayer.dataProvider()
        selectProvider = selectLayer.dataProvider()
        feat = QgsFeature()
        infeat = QgsFeature()
        geom = QgsGeometry()
        selectedSet = []
        index = ft.createIndex(inputProvider)

        selectFit = selectProvider.getFeatures()
        while selectFit.nextFeature(feat):
                geom = QgsGeometry(feat.geometry())
                intersects = index.intersects(geom.boundingBox())
                for id in intersects:
                    inputProvider.getFeatures( QgsFeatureRequest().setFilterFid( int(id) ) ).nextFeature( infeat )
                    tmpGeom = QgsGeometry( infeat.geometry() )
                    if geom.intersects(tmpGeom):
                        selectedSet.append(infeat.id())

        outputSelection = inputLayer.setSelectedFeatures(selectedSet)


        vectorLayer = processing.getObject(inputLayer.name())
        provider = vectorLayer.dataProvider()
        fields = provider.fields()


        newName = 'selectedGrid'

        newlayer = QgsVectorLayer("MultiPolygon", "temporary_selection", "memory")

        pr = newlayer.dataProvider()

        pr.addAttributes(fields.toList())
        newlayer.startEditing()


        features = processing.features(vectorLayer)
        for feat in features:
            newlayer.addFeature(feat)

        return newlayer

def dirDialog(parent):
    settings = QSettings()
    dirName = settings.value("")
    encode = settings.value("")
    fileDialog = QgsEncodingFileDialog(parent, "Browse a directory", dirName, encode)
    fileDialog.setFileMode(QFileDialog.DirectoryOnly)
    fileDialog.setAcceptMode(QFileDialog.AcceptSave)
    fileDialog.setConfirmOverwrite(False)
    if not fileDialog.exec_() == QDialog.Accepted:
            return None, None
    folders = fileDialog.selectedFiles()
    settings.setValue("", QFileInfo(unicode(folders[0])).absolutePath())
    return (unicode(folders[0]), unicode(fileDialog.encoding()))
    print 'Ecco la DIR --------------->>> ', fileDialog.encoding()

def fileDialog(parent):

    myfile = QFileDialog.getOpenFileName(parent, "Choose a file", "", "")
    fileInfo = QFileInfo(myfile)

    return unicode(fileInfo.canonicalFilePath()) # fileName()

def copyVectorFields(layerFrom, layerTo, fieldsList):
    # Copy field(s) value from a vector to field(s) of a target vector
    # layerFrom = Name of origin layer
    # layerTo   = Name of target layer
    # fieldsList = [('fieldnameFrom1', 'fieldnameTo1'), ('fieldnameFrom2', 'fieldnameTo2'), ... ,
    #                  , .... , ('fieldnameFromN', 'fieldnameToN')]
    layerFrom = QgsMapLayerRegistry.instance().mapLayersByName(layerFrom)[0]
    layerTo = QgsMapLayerRegistry.instance().mapLayersByName(layerTo)[0]
    layerFrom.dataProvider().createSpatialIndex()
    layerTo.dataProvider().createSpatialIndex()

    changedAttributesDict = {}

    for toFeat in layerTo.getFeatures():
        toGeom = toFeat.geometry()
        toBbox = toGeom.boundingBox()
        fromRequest = QgsFeatureRequest(toBbox)
        fromRequest.setFlags(QgsFeatureRequest.ExactIntersect)
        maxArea = -1
        sourceFromFeat = None
        for fromFeat in layerFrom.getFeatures(fromRequest):
            fromGeom = fromFeat.geometry()
            intersectGeom = toGeom.intersection(fromGeom)
            if not intersectGeom:
                continue
            if not intersectGeom.isGeosValid():
                continue
            currentArea = intersectGeom.area()
            if maxArea < currentArea:
                sourceFromFeat = fromFeat
                maxArea = currentArea
        changedAttributes = {}
        if sourceFromFeat is not None:
            for fieldFrom, fieldTo in fieldsList:
                destIdx = layerTo.dataProvider().fieldNameIndex(fieldTo)
                valueToCopy = sourceFromFeat[fieldFrom]
                changedAttributes[destIdx] = valueToCopy
            changedAttributesDict[toFeat.id()] = changedAttributes

    layerTo.dataProvider().changeAttributeValues(changedAttributesDict)
    layerTo.updateFields()

def getRasterNames():
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    layerNames = []
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.RasterLayer:
            layerNames.append(str(layer.name()))
    return layerNames


def getRasterByName(layerName):
    layerMap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layerMap.iteritems():
        if layer.type() == QgsMapLayer.RasterLayer and layer.name() == layerName:
            if layer.isValid():
                return layer
            else:
                return None

##def copyRasterToField_rasterizeMethod(inputGrid, inputRaster, outField="Z"):
##    # Open data
##    gridLayer = QgsMapLayerRegistry.instance().mapLayersByName(inputGrid)[0]
##    # Open OGR layer for gdal.RasterizeLayer
##    print "%s" % str(gridLayer.source())
##    ds = ogr.Open("%s" % str(gridLayer.source()))
##    lyr = ds.GetLayer()
##    print lyr.GetName()
##    geometryType = gridLayer.wkbType()
##
##    if geometryType != QGis.WKBPolygon:
##        return
##
##    rasterLayer = QgsMapLayerRegistry.instance().mapLayersByName(inputRaster)[0]
##    raster = gdal.Open(rasterLayer.source(), gdal.GA_ReadOnly)
##
##    transform = raster.GetGeoTransform()
##    xOrigin = transform[0]
##    yOrigin = transform[3]
##    pixelWidth = transform[1]
##    pixelHeight = transform[5]
##
##    raster_srs = osr.SpatialReference()
##    raster_srs.ImportFromWkt(raster.GetProjectionRef())
##    banddataraster = raster.GetRasterBand(1)
##
##    for cell in gridLayer.getFeatures():
##        cellBBOX = cell.geometry().boundingBox()
##
##        xmin = cellBBOX.xMinimum()
##        xmax = cellBBOX.xMaximum()
##        ymin = cellBBOX.yMinimum()
##        ymax = cellBBOX.yMaximum()
##
##        xoff = int((xmin - xOrigin)/pixelWidth)
##        yoff = int((yOrigin - ymax)/pixelWidth)
##        xcount = int((xmax - xmin)/pixelWidth)+1
##        ycount = int((ymax - ymin)/pixelWidth)+1
##
##        if xoff > 0 and yoff > 0:
##            target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
##            target_ds.SetGeoTransform((xmin, pixelWidth, 0, ymax, 0, pixelHeight,))
##            target_ds.SetProjection(raster_srs.ExportToWkt())
##            gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])
##
##            dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
##            bandmask = target_ds.GetRasterBand(1)
##            datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)
##            zoneraster = numpy.ma.masked_array(dataraster,  numpy.logical_not(datamask))
##
##            print numpy.mean(zoneraster)
##            target_ds = None


def copyRasterToField(inputGrid, inputRaster, outField_name="Z", precise=False):
    # Open data
    gridLayer = QgsMapLayerRegistry.instance().mapLayersByName(inputGrid)[0]
    geometryType = gridLayer.geometryType()

    if geometryType != 2:
        raise Exception("Input vector must be polygon")

    fieldIdx = gridLayer.fieldNameIndex(outField_name)

    if fieldIdx == -1:
        raise Exception("%s field does not exist" % outField_name)

    outField = gridLayer.dataProvider().fields()[fieldIdx]

    if outField.type() != QVariant.Double:
        raise Exception("%s field type must be Double" % outField_name)

    rasterLayer = QgsMapLayerRegistry.instance().mapLayersByName(inputRaster)[0]
    rasterBBox = rasterLayer.extent()
    xOrigin = rasterBBox.xMinimum()
    yOrigin = rasterBBox.yMaximum()
    cellSizeX = rasterLayer.rasterUnitsPerPixelX()
    cellSizeY = rasterLayer.rasterUnitsPerPixelY()
    nCellsXGDAL = rasterLayer.width()
    nCellsYGDAL = rasterLayer.height()

    gridLayer.startEditing()

    for gridCell in gridLayer.getFeatures():
        gridCellBBOX = gridCell.geometry().boundingBox()
        featureBBox = gridCellBBOX.intersect(rasterBBox)
        if featureBBox.isEmpty():
            continue

        offsetX,offsetY,nCellsX,nCellsY = cellInfoForBBox(featureBBox, rasterBBox, cellSizeX, cellSizeY)

        if (( offsetX + nCellsX ) > nCellsXGDAL ):
          nCellsX = nCellsXGDAL - offsetX
        if (( offsetY + nCellsY ) > nCellsYGDAL ):
          nCellsY = nCellsYGDAL - offsetY

        valueSum, count = statisticsFromMiddlePointTest(rasterLayer, gridCell.geometry(), offsetX, offsetY,
                                                        nCellsX, nCellsY, cellSizeX, cellSizeY, precise)
        mean = valueSum/count

        gridLayer.changeAttributeValue(gridCell.id(), fieldIdx, mean)

        #print valueSum,valueSum/count,count

    gridLayer.commitChanges()


def cellInfoForBBox(featureBBox, rasterBBox, cellSizeX, cellSizeY):
    offsetX = (featureBBox.xMinimum() - rasterBBox.xMinimum()) / cellSizeX
    offsetY = (rasterBBox.yMaximum() - featureBBox.yMaximum()) / cellSizeY

    maxColumn = ((featureBBox.xMaximum() - rasterBBox.xMinimum()) / cellSizeX) + 1
    maxRow = ((rasterBBox.yMaximum() - featureBBox.yMinimum()) / cellSizeY) + 1

    nCellsX = maxColumn - offsetX
    nCellsY = maxRow - offsetY

    return int(offsetX), int(offsetY), int(nCellsX), int(nCellsY)


def statisticsFromMiddlePointTest(rasterLayer, poly, pixelOffsetX, pixelOffsetY,
                                  nCellsX, nCellsY, cellSizeX, cellSizeY, precise):
    rasterBBox = rasterLayer.extent()
    polyRectAligned_xmin = rasterBBox.xMinimum() + (pixelOffsetX * cellSizeX)
    polyRectAligned_ymin = rasterBBox.yMaximum() - (pixelOffsetY * cellSizeY) - (nCellsY * cellSizeY)
    polyRectAligned_xmax = rasterBBox.xMinimum() + (pixelOffsetX * cellSizeX) + (nCellsX * cellSizeX)
    polyRectAligned_ymax = rasterBBox.yMaximum() - (pixelOffsetY * cellSizeY)
    polyRectAligned = QgsRectangle(polyRectAligned_xmin, polyRectAligned_ymin,
                                   polyRectAligned_xmax, polyRectAligned_ymax)

    cellsBlock = rasterLayer.dataProvider().block(1, polyRectAligned, nCellsX, nCellsY)
    valuesSum = 0.0
    count = 0

    cellCenterY = rasterBBox.yMaximum() - pixelOffsetY * cellSizeY - cellSizeY / 2
    for y in range(nCellsY):
        cellCenterX = rasterBBox.xMinimum() + pixelOffsetX * cellSizeX + cellSizeX / 2
        for x in range(nCellsX):
            keep = True
            if precise:
                keep = False
                cellCenter = QgsPoint(cellCenterX, cellCenterY)
                if poly.contains(cellCenter):
                    keep = True
            if keep:
                val = cellsBlock.value(y, x)
                if not math.isnan(val):
                    valuesSum += val
                count += 1
            cellCenterX += cellSizeX
        cellCenterY -= cellSizeY

    return valuesSum, count

def statisticsFromPreciseIntersection():
    pass

# --
def createAttributes(vectorLayer, fields):
    provider = vectorLayer.dataProvider()
    fieldsToCreate = []
    for field in fields:
        if provider.fieldNameIndex(field) != -1:
            continue
        else:
            print "New field %s" % field
            new_field = QgsField(field, QVariant.Double)
            fieldsToCreate.append(new_field)
    provider.addAttributes(fieldsToCreate)
    # hack to update fields
    vectorLayer.startEditing()
    vectorLayer.commitChanges()
# ---
def getModelsInfoLists(layerNameList):
    # From the list of layers loaded in QGis TOC, search for modeltable_ layers
    # and retrieve model names and working path
    # OUTPUT: a tuple of 2 lists

    isok = 0
    modelNameList = []
    pathList = []
    for mName in layerNameList:
        if mName[0:10] == 'modeltable':
            isok = 1
            modelNameTable = getVectorLayerByName(mName)
            for f in modelNameTable.getFeatures():
                nameTemp = f['name']
                pathTemp = f['working_dir']
                modelNameList.append(nameTemp)
                pathList.append(pathTemp)
    ## Message Error if no model is found
    if isok == 0:
        QMessageBox.warning(self, self.tr('No model found!!'),
                            self.tr('There is no model table in TOC '
                                    'You have to create a MODEL before '
                                    'running Model Layer Creation ' ))
    if isok >= 1:
        return (modelNameList, pathList)
# --
def getModelInfoByName(modelName):
    # from the model name, get relative Working Path and number of stress periods
    layerNameList = getVectorLayerNames()
    (modelNameList, pathList) = getModelsInfoLists(layerNameList)
    i = 0;
    for mName in modelNameList:
        if mName ==  modelName:
           pathfile = pathList[i]
        i = i+1

    timelayer = getVectorLayerByName('timetable_' + modelName)
    ftit = timelayer.getFeatures()
    nsp = 0
    for i in ftit:
        nsp = nsp + 1

    return (pathfile, nsp)

