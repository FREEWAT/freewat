# Crea nuovo layer come copia del layer attivo, ma shape file diverso
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from pyspatialite import dbapi2 as sqlite3
import processing
from freewat_utils import getVectorLayerByName, createAttributes
from freewat_formulas import cond, lerp
from sqlite_utils import uploadQgisVectorLayer, checkIfTableExists
import sys, os


# ---------------------------
# Create a new MODEL: its DB SQLite, along with its modeltable and its timetable
def createModel(modelname, workingDir, modeltype, isChild, lengthString, timeString):

    # Set file name

    dbname = workingDir + '/' + modelname + ".sqlite"
    # creating/connecting SQL database object
    con = sqlite3.connect(dbname)
    # con = sqlite3.connect(":memory:") if you want write it in RAM
    con.enable_load_extension(True)
    cur = con.cursor()
    # Initialise spatial db
    # Insert a control for existing table or not
    cur.execute("PRAGMA foreign_keys = ON")
    # cur.execute("SELECT load_extension('libspatialite.so.5');")
    # Initializing Spatial MetaData: GEOMETRY_COLUMNS and SPATIAL_REF_SYS
    cur.execute("SELECT InitSpatialMetaData(1);")


    # Create new model table

    if lengthString == 'undefined':
        lengthUnit = 0
    elif lengthString == 'ft':
        lengthUnit = 1
    elif lengthString == 'm':
        lengthUnit = 2
    elif lengthString == 'cm':
        lengthUnit = 3

    if timeString == 'undefined':
        timeUnit = 0
    elif timeString == 'sec':
        timeUnit = 1
    elif timeString == 'min':
        timeUnit = 2
    elif timeString == 'hour':
        timeUnit = 3
    elif timeString == 'day':
        timeUnit = 4
    elif timeString == 'year':
        timeUnit = 5

    # Create new SQL table

    modeltableName = 'modeltable_' + modelname

    SQLstring = 'CREATE TABLE "%s" ("name" varchar(20), "type" varchar(20),' \
                '"length_unit" integer, "time_unit" integer, "is_child" integer, ' \
                '"working_dir" varchar(99));'%modeltableName

    cur.execute(SQLstring)

    cur.execute("SELECT AddGeometryColumn('%s', 'the_geom', 4326, 'POINT', 'XY');"%modeltableName)

    # Insert values in Model Table
    parameters = [modelname, modeltype, lengthUnit, timeUnit, isChild, workingDir]
    sqlstr = 'INSERT INTO %s'%modeltableName
    cur.execute(sqlstr + ' (name,type,length_unit,time_unit,is_child,working_dir) VALUES (?, ?, ?, ?, ?, ?);', (parameters[0], parameters[1], parameters[2], parameters[3], parameters[4], parameters[5]))

    # Create and initialize the model time table
    # Create new SQL table
    timeName = 'timetable_%s'%modelname

    sql2 = 'CREATE TABLE "%s" '%timeName
    sql22 = sql2 + ' ("id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "sp" SERIAL INTEGER NOT NULL, "length" float, "ts" integer, "multiplier" float, "state" varchar(4) );'

    cur.execute(sql22)

    sql3 = " SELECT AddGeometryColumn( '%s', 'the_geom', 4326, 'POINT', 'XY'); "%timeName
    cur.execute(sql3)

    # Initialize values in Model Table
    parameters2 = [1, 1, 365.0, 1, 1.0, 'SS']
    sql4 = 'INSERT INTO %s'%timeName
    sql44 = sql4 + '   (id, sp, length, ts, multiplier, state) VALUES (?, ?, ?, ?, ?, ?);'

    cur.execute(sql44, (parameters2[0], parameters2[1], parameters2[2], parameters2[3], parameters2[4], parameters2[5] ))
    # Close cursor
    cur.close()
    # Save the changes
    con.commit()
    # Close connection
    con.close()

    # Add the model table into QGis map
    uri = QgsDataSourceURI()
    uri.setDatabase(dbname)
    schema = ''
    table = modeltableName
    geom_column = 'the_geom'
    uri.setDataSource(schema, table, geom_column)
    display_name = modeltableName
    tableLayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')

    QgsMapLayerRegistry.instance().addMapLayer(tableLayer)


     # Add the model time table into QGis map
    uri2 = QgsDataSourceURI()
    uri2.setDatabase(dbname)
    uri2.setDataSource(schema, timeName, geom_column)
    display_name2 = timeName
    timeLayer = QgsVectorLayer(uri2.uri(), display_name2, 'spatialite')

    QgsMapLayerRegistry.instance().addMapLayer(timeLayer)

# Create a new MDO layer
def createMDO(gridLayer, dbName, newName, fieldNameList, fieldTypeList, fieldDefaultList):

# Old version:
##    # Create a copy of Grid Layer as temporary layer
##    # (using processing algorithm only selected features (if any) are used instead of the whole gridLayer
##
##    provider = gridLayer.dataProvider() #provider = vectorLayer.dataProvider()
##
##    # Check if a table with this name already exists in DB
##    control = checkIfTableExists(dbName,newName, popupExists = True )
##    if control == True:
##        return
##
##    # Upload a copy of the grid layer into DB SQlite (before: check if selection exits)
###    if gridLayer.selectedFeatureCount()==0:
##        uploadQgisVectorLayer(dbName, gridLayer, newName, srid=None, selected=False, mapinfo=True)
###    if gridLayer.selectedFeatureCount() > 0:
###        uploadQgisVectorLayer(dbName, gridLayer, newName, srid=None, selected=True, mapinfo=True)
##
##    # Retrieve the Spatialite layer and create a new QgsVectorLayer
##    uri = QgsDataSourceURI()
##    uri.setDatabase(dbName)
##    schema = ''
##    table = newName
##    geom_column = "Geometry"
##    uri.setDataSource(schema, table, geom_column)
##    display_name = newName
##    newlayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
##    dp = newlayer.dataProvider()
##
##    newlayer.startEditing()
##    # Add new fields
##    for i in range(0, len(fieldNameList)):
##        newfield = QgsField(fieldNameList[i], fieldTypeList[i])
##        res = dp.addAttributes( [newfield] )
##    newlayer.updateFields()
##
##
##
##    # Add default values for new fields
##    fields = newlayer.dataProvider().fields()
##    idval = 0
##    for field in fieldNameList:
##        idx = fields.indexFromName(field)#retrieve field index from name
##        for f in newlayer.getFeatures():
##            attrs = f.attributes()
##            for attr in attrs:
##                feat = f.id()
##                newlayer.changeAttributeValue(feat, idx, fieldDefaultList[idval])
##        idval += 1
##
##    newlayer.commitChanges()
##
##
##    # Add new layer to Qgis MAp
##
##    QgsMapLayerRegistry.instance().addMapLayer(newlayer)

    # New version:
        # Create a copy of Grid Layer as temporary layer
    # (using processing algorithm only selected features (if any) are used instead of the whole gridLayer

    provider = gridLayer.dataProvider() #provider = vectorLayer.dataProvider()

    vl = QgsVectorLayer("Polygon", "temporary_points", "memory")
    pr = vl.dataProvider()
    fld = gridLayer.dataProvider().fields()

    idfield = 0
    for f in fld:
    	pr.addAttributes([f])

    for feature in processing.features(gridLayer):
        att = feature.attributes()
        pr.addFeatures([feature])
    vl.commitChanges()
    vl.startEditing()

    # Add new fields
    for i in range(0, len(fieldNameList)):
        newfield = QgsField(fieldNameList[i], fieldTypeList[i])
        res = pr.addAttributes( [newfield] )
    vl.updateFields()

    # Add default values for new fields
    fields = vl.dataProvider().fields()
    idval = 0
    for field in fieldNameList:
        idx = fields.indexFromName(field)#retrieve field index from name
        for f in vl.getFeatures():
            attrs = f.attributes()
            for attr in attrs:
                feat = f.id()
                vl.changeAttributeValue(feat, idx, fieldDefaultList[idval])
        idval += 1

    vl.commitChanges()




##    for field in fieldNameList:
##        idx = fields.indexFromName(field)#retrieve field index from name
##        for f in newlayer.getFeatures():
##            attrs = f.attributes()
##            for attr in attrs:
##                feat = f.id()
##                newlayer.changeAttributeValue(feat, idx, fieldDefaultList[idval])
##        idval += 1
##
##


##    for i in range(0, len(fieldNameList)):
##        newfield = QgsField(fieldNameList[i], fieldTypeList[i])
##        # TO DO: Qui vorrei capire come inserire un valore di default del campo.
##        res = dp.addAttributes( [newfield] )
##    newlayer.updateFields()
##
##    newlayer.startEditing()
##    fields = newlayer.dataProvider().fields()
##    idval = 0
##    for field in fieldNameList:
##        idx = fields.indexFromName(field)#retrieve field index from name
##        for f in newlayer.getFeatures():
##            attrs = f.attributes()
##            for attr in attrs:
##                feat = f.id()
##                newlayer.changeAttributeValue(feat, idx, fieldDefaultList[idval])
##        idval += 1
##
##    newlayer.commitChanges()
##

    # Upload the vlayer into DB SQlite
    uploadQgisVectorLayer(dbName, vl, newName)

    # Retrieve the Spatialite layer and add it to mapp
    uri = QgsDataSourceURI()
    uri.setDatabase(dbName)
    schema = ''
    table = newName
    geom_column = "Geometry"
    uri.setDataSource(schema, table, geom_column)
    display_name = table

    wlayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')

    QgsMapLayerRegistry.instance().addMapLayer(wlayer)
##
##    # Delate the temporary shape file
##    os.remove(temporaryfile)


# --- Create a Model Layer and create (or update) LPF table

def createModelLayer(gridLayer, pathFile, modelname, layerName, parameters):

    name_fields = ['BORDER' ,'ACTIVE','TOP', 'BOTTOM', 'STRT', 'KX', 'KY', 'KZ', 'SS', 'SY', 'NT', 'NE', 'DRYWET']
    type_fields = [QVariant.Int , QVariant.Int, QVariant.Double,  QVariant.Double , QVariant.Double, QVariant.Double, QVariant.Double, QVariant.Double, QVariant.Double, QVariant.Double, QVariant.Double, QVariant.Double, QVariant.Double ]

    dbName = pathFile + '/' + modelname + '.sqlite'

    default_fields = [0, 1, parameters[5], parameters[6], 1.0, 0.001, 0.001, 0.0001, 0.1, 0.001, 1, 1, 0]

    createMDO(gridLayer,dbName,layerName, name_fields, type_fields, default_fields)



    # Create or update LPF table of the Model
    nameTable = "lpf_"+ modelname

    # Convert info into MODLFOW flags:
    layType    = parameters[1]
    layAverage  = parameters[2]
    chani   = parameters[3]
    layWet  = parameters[4]

    # Define values of new feature for LPF
    # -- Create list ft
    ft = [layerName,layType, layAverage,chani,layWet]
    # --
    #Convert in a tuple
    ftinsert = tuple(ft)

    # Check if LPF table exists:
    lpflayer = getVectorLayerByName(nameTable)


    if lpflayer == None :
        # Connect to DB
        # creating/connecting SQL database object
        con = sqlite3.connect(dbName)
        # con = sqlite3.connect(":memory:") if you want write it in RAM
        con.enable_load_extension(True)
        cur = con.cursor()
        # Create new LPF table in DB
        SQLcreate = 'CREATE TABLE %s ("name" varchar(20), "type" integer,' \
                '"layavg" integer, "chani" integer, "laywet" integer );'% nameTable

        cur.execute(SQLcreate)
        sql2 = "SELECT AddGeometryColumn( '%s', 'Geometry', 4326, 'POINT', 'XY');"% nameTable
        cur.execute(sql2)

        # Insert values in Table
        sql3 = 'INSERT INTO %s '%nameTable +  '(name,type,layavg,chani,laywet)'

        cur.execute(sql3 + 'VALUES (?, ?, ?, ?, ?);', ftinsert)
        # Close SpatiaLiteDB
        cur.close()
        # Save the changes
        con.commit()
        # Close connection
        con.close()


        # Retrieve the Spatialite layer and add it to mapp
        uri = QgsDataSourceURI()
        uri.setDatabase(dbName)
        schema = ''
        table = nameTable
        geom_column = "Geometry"
        uri.setDataSource(schema, table, geom_column)
        display_name = nameTable

        wlayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')

        QgsMapLayerRegistry.instance().addMapLayer(wlayer)

    else:
        # Update existing LPF table
        # Add features related to the new model layer
        dp = lpflayer.dataProvider()
        fields = lpflayer.pendingFields()
        ftnew = QgsFeature(fields)
        for i in range(0,len(ft)):
            ftnew[i] = ft[i]

        dp.addFeatures( [ ftnew ] )

# --- Create a CHD Layer
def createChdLayer(gridLayer, name, pathFile, modelName, nsp):

    layerName = name + "_chd"
    dbName = pathFile + '/' + modelName + '.sqlite'

    name_fields = []
    type_fields = []

    name_fields.append('from_lay')
    type_fields.append(QVariant.Int)
    name_fields.append('to_lay')
    type_fields.append(QVariant.Int)

    # Initialize Default values for fields:
    default_fields = [1 , 1]

    for i in range(1,nsp+1):
        name_fields.append(str(i) + '_shead')
        type_fields.append(QVariant.Double)
        default_fields.append(10)

        name_fields.append(str(i) + '_ehead')
        type_fields.append(QVariant.Double)
        default_fields.append(10)

    # Create MDO for CHD:
    createMDO(gridLayer, dbName, layerName, name_fields, type_fields, default_fields)

# ---------------------------
# --- Create a Well Layer
def createWellLayer(gridLayer, name, pathFile, modelName, nsp):

    layerName = name + "_well"
    dbName = pathFile + '/' + modelName + '.sqlite'

    name_fields = []
    type_fields = []

    name_fields.append('from_lay')
    type_fields.append(QVariant.Int)
    name_fields.append('to_lay')
    type_fields.append(QVariant.Int)
    name_fields.append('active')
    type_fields.append(QVariant.Int)

    default_fields = [1,1,1]

    for i in range(1,nsp+1):
        name_fields.append('sp_'+ str(i) )
        type_fields.append(QVariant.Double)
        default_fields.append(-100)


    # Create MDO for WEL:
    createMDO(gridLayer, dbName, layerName, name_fields, type_fields, default_fields)

# ---------------------------
# --- Create a RCH Layer
def createRchLayer(gridLayer, name, pathFile, modelName, nsp):

    layerName = name + "_rch"
    dbName = pathFile + '/' + modelName + '.sqlite'
    #
    name_fields = []
    type_fields = []
    default_fields = []

    for i in range(1,nsp+1):
        name_fields.append( 'sp_' + str(i) + '_rech')
        type_fields.append(QVariant.Double)
        default_fields.append(0.01)

        name_fields.append('sp_' + str(i) + '_irch')
        type_fields.append(QVariant.Int)
        default_fields.append(1)



    createMDO(gridLayer, dbName, layerName, name_fields, type_fields, default_fields)
# ---------------------------

# --- Create a River Layer
def createRivLayer(newName, dbName, gridLayer, riverLayer, csvlayer, width, layer, xyz, nsp ):
    # --- Input:
    # newName: name of the new MDO for river
    # dbName: name of model DB (complete path)
    # gridLayer: grid layer
    # csvlayer: csv table with parameters (for each stress period)
    #           [sp, rh_in, rh_out, bt_in, bt_out, krb_in, krb_out, thk_in, thk_out]
    # river: line layer
    # width: river width, given as scalar (constant)
    # layer: layer where RIV is applied  (integer)
    # xyz: river segment id (integer)
    # nsp: stress period number

    # Check if river layer has the correct format
    # To do: change check of Wkb into Geometry type

    if riverLayer.wkbType() != 2:
        raise Exception("Input river layer must by single part linestring")

    if riverLayer.featureCount() > 1:
        raise Exception("Input river layer must contain only one feature")

    ##
    # trasformo csv layer in dictionary
    dp = csvlayer.dataProvider()
    csv_dict = {}

    i = 0
    for f in csvlayer.getFeatures():
        ft_lst = []
        for fld in dp.fields():
            ft_lst.append(f[fld.name()])
        del fld
        csv_dict[i+1] = ft_lst[1:]
        i += 1
    # ---

    # Create a copy of Grid Layer as temporary layer
    #
    provider = gridLayer.dataProvider()
    grid = QgsVectorLayer("Polygon", "temporary_layer", "memory")
    pr = grid.dataProvider()

    # fields of original grid layer
    fld = gridLayer.dataProvider().fields()
    for f in fld:
    	pr.addAttributes([f])
    # features from the original grid layer
    for feature in processing.features(gridLayer):
        att = feature.attributes()
        pr.addFeatures([feature])

    grid.startEditing()
    grid.commitChanges()

    # Add the new fields 'layer' and 'xyz' (Integer)
    newfield = QgsField('layer', QVariant.Int)
    pr.addAttributes( [newfield] )
    newfield = QgsField('xyz', QVariant.Int)
    pr.addAttributes( [newfield] )


    # Define List of new fields name
    fieldsList = ['length']
    for i in range(1,nsp+1):
        fieldsList.append('stage_'+ str(i) )
        fieldsList.append('rbot_'+ str(i) )
        fieldsList.append('cond_'+ str(i) )




    # Call the method to write new fields to be added
    createAttributes(grid, fieldsList)

    #  Start editing to write record
    grid.startEditing()

    changedAttributesDict = {}
    #
    ft_sel_id = []
    for feature in grid.getFeatures():
        gridPoly = feature.geometry()
        inCellRiverLength = 0.0
        inCoeff = 0.0
        outCoeff = 0.0
        # I take the only one river
        riverFeature = [f for f in riverLayer.getFeatures(QgsFeatureRequest(0))][0]
        riverLine = riverFeature.geometry()
        riverLength = riverLine.length()
        riverPoints = riverLine.asPolyline()
        #
        if riverLine.intersects(gridPoly):
            #
            ft_sel_id.append(feature.id())
            #
            inCellRiver = riverLine.intersection(gridPoly)
            # print "Grid ID %s - River %s - Lenght in cell: %s" % (feature.id(),riverFeature.id(),inCellRiver.length())
            if inCellRiver.wkbType() == QGis.WKBLineString:
                linepoints = inCellRiver.asPolyline()
                # first point
                pointIn = linepoints[0]
                # last point
                pointOut = linepoints[len(linepoints)-1]
                #print "Ingresso: %s %s" % (pointIn.x(),pointIn.y())
                #print "Uscita: %s %s" % (pointOut.x(),pointOut.y())
            elif inCellRiver.wkbType() == QGis.WKBMultiLineString:
                multilinepoints = inCellRiver.asMultiPolyline()
                # first point of first list
                pointIn = multilinepoints[0][0]
                lastGroup = multilinepoints[len(multilinepoints)-1]
                # last point of last list
                pointOut = lastGroup[len(lastGroup)-1]
                #print "Ingresso: %s %s" % (pointIn.x(),pointIn.y())
                #print "Uscita: %s %s" % (pointOut.x(),pointOut.y())

            _, _, beforeVertexIndexpointIn, _, _ = riverLine.closestVertex(QgsPoint(pointIn))
            _, _, beforeVertexIndexpointOut, _, _ = riverLine.closestVertex(QgsPoint(pointOut))
            beforeVertexpointIn = riverPoints[beforeVertexIndexpointIn]
            beforeVertexpointOut = riverPoints[beforeVertexIndexpointOut]
            #print "Indice vertice precedente Ingresso: %s" % (beforeVertexIndexpointIn)
            #print "Indice vertice precedente Uscita: %s" % (beforeVertexIndexpointOut)
            if beforeVertexIndexpointIn == -1:
                beforeVertexpointIn = pointIn
            if beforeVertexIndexpointOut == -1:
                beforeVertexpointOut = pointOut
            #print "Vertice precedente Ingresso: %s %s" % (beforeVertexpointIn.x(),beforeVertexpointIn.y())
            #print "Vertice precedente Uscita: %s %s" % (beforeVertexpointOut.x(),beforeVertexpointOut.y())

            if beforeVertexIndexpointIn == -1:
                beforeVertexIndexpointIn = 0
            if beforeVertexIndexpointOut == -1:
                beforeVertexIndexpointOut = 0

            stretchIn = riverPoints[0: beforeVertexIndexpointIn+1]
            stretchIn.append(pointIn)
            stretchInGeom = QgsGeometry.fromPolyline(stretchIn)
            currentInLength = stretchInGeom.length()
            stretchOut = riverPoints[0: beforeVertexIndexpointOut+1]
            stretchOut.append(pointOut)

##            try:
            stretchOutGeom = QgsGeometry.fromPolyline(stretchOut)
            currentOutLength = stretchOutGeom.length()
            inCoeff = currentInLength / riverLength
            outCoeff = currentOutLength / riverLength
##                print "Parziale ingresso: %s" % (currentInLength)
##                print "Parziale uscita: %s" % (currentOutLength)
##                print "Coefficiente interpolazioni ingresso: %s" % (float(currentInLength)/riverLine.length())
##                print "Coefficiente interpolazioni ingresso: %s" % (float(currentOutLength)/riverLine.length())
##                print "Grid ID: %s" % (feature.id())
            changedAttributes = {}
            # Insert value to layer field (layer)
            fieldIdx = grid.dataProvider().fieldNameIndex('layer')
            changedAttributes[fieldIdx] = layer

            # Insert value to xyz field (xyz)
            fieldIdx = grid.dataProvider().fieldNameIndex('xyz')
            changedAttributes[fieldIdx] = xyz

            # Insert value to length field
            fieldIdx = grid.dataProvider().fieldNameIndex('length')
            changedAttributes[fieldIdx] = inCellRiver.length()
            Lreach = inCellRiver.length()

            for sp, field in csv_dict.iteritems():
                # rh_in, rh_out, bt_in, bt_out, krb_in, krb_out, thk_in, thk_out
                # river head
                valueIn = field[0]
                valueOut = field[1]
                valueIn_int = lerp(valueIn, valueOut, inCoeff)
                valueOut_int = lerp(valueIn, valueOut, outCoeff)
                avg = (valueIn_int + valueOut_int)/2

                fieldIdx = grid.dataProvider().fieldNameIndex('stage_%i' % sp)
                changedAttributes[fieldIdx] = avg

                # river bottom
                valueIn = field[2]
                valueOut = field[3]
                valueIn_int = lerp(valueIn, valueOut, inCoeff)
                valueOut_int = lerp(valueIn, valueOut, outCoeff)
                avg = (valueIn_int + valueOut_int)/2

                fieldIdx = grid.dataProvider().fieldNameIndex('rbot_%i' % sp)
                changedAttributes[fieldIdx] = avg

                # river thickness
                valueIn = field[6]
                valueOut = field[7]
                valueIn_int = lerp(valueIn, valueOut, inCoeff)
                valueOut_int = lerp(valueIn, valueOut, outCoeff)
                th_avg = (valueIn_int + valueOut_int)/2

                # river conductance
                valueIn = field[4]
                valueOut = field[5]
                valueIn_int = lerp(valueIn, valueOut, inCoeff)
                valueOut_int = lerp(valueIn, valueOut, outCoeff)
                avg = (valueIn_int + valueOut_int)/2

                cnd = cond(avg,Lreach,width,th_avg)

                fieldIdx = grid.dataProvider().fieldNameIndex('cond_%i' % sp)
                changedAttributes[fieldIdx] = cnd


            changedAttributesDict[feature.id()] = changedAttributes
##            except:
##                pass
                #print "Errore FID: %s" % feature.id()

    grid.dataProvider().changeAttributeValues(changedAttributesDict)
    grid.commitChanges()

    # Select only intersected cells (whose IDs are in ft_sel_id)
    grid.select(ft_sel_id)


    # Upload the vlayer into DB SQlite
    newName = newName + '_riv'
    uploadQgisVectorLayer(dbName, grid, newName, srid= grid.crs().postgisSrid(), selected = True )

    # Retrieve the Spatialite layer and add it to mapp
    uri = QgsDataSourceURI()
    uri.setDatabase(dbName)
    schema = ''
    table = newName
    geom_column = "Geometry"
    uri.setDataSource(schema, table, geom_column)
    display_name = table

    wlayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')

    QgsMapLayerRegistry.instance().addMapLayer(wlayer)
# ---------------------------




# ---------------------------
# DA QUI ROBA VECCHIA !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ---------------------------
# OLD VERSION (NOT WORKING!!) FROM HERE


# ---------------------------
# --- Create a Transport Layer
def createTransportLayer(gridLayer, pathFile, modelName, nlay, nspec, ireact):

    newname = "transport_layer_"
    name_fields = []
    type_fields = []
    for i in range(1,nlay+1):
        name_fields.append('AL_'+ str(i) )
        type_fields.append(QVariant.Double)
        name_fields.append('TRPT_' + str(i))
        type_fields.append(QVariant.Double)
        name_fields.append('TRPV_' + str(i))
        type_fields.append(QVariant.Double)

        for j in range(1,nspec +1):
            name_fields.append('SCONC_' + str(i) + '_' + str(j) )
            type_fields.append(QVariant.Double)

            name_fields.append('DMCOEF_' + str(i) + '_' +  str(j) )
            type_fields.append(QVariant.Double)

            if ireact > 0:
                name_fields.append('RC1_' + str(i) + '_' + str(j) )
                type_fields.append(QVariant.Double)

                name_fields.append('RC2_' + str(i) + '_' +  str(j) )
                type_fields.append(QVariant.Double)


    layerName = newname + modelName
    newfile   = pathFile +  layerName + ".shp"

    createMDO(gridLayer, newfile, layerName, name_fields, type_fields)
#
# --- Create a Source Sink Layer
def createSourceLayer(gridLayer, pathFile, modelName, nsp, nlay, nspec, incrch, incevt, nss):

    newname = "source_layer_"
    name_fields = []
    type_fields = []


    for k in range(1,nsp+1):
         if incrch == 'T':
            for j in range(1,nspec +1):
                name_fields.append('CRCH_'+ str(k) + '_' + str(j) )
                type_fields.append(QVariant.Double)
         if incevt == 'T':
            for j in range(1,nspec +1):
                name_fields.append('CEVT_'+ str(k) + '_' + str(j) )
                type_fields.append(QVariant.Double)
         if nss > 0:
            for j in range(1,nspec +1):
                name_fields.append('CSS_'+ str(k) + '_' + str(j) )
                type_fields.append(QVariant.Double)
                name_fields.append('ITAPE_'+ str(k) + '_' + str(j) )
                type_fields.append(QVariant.Int)

    layerName = newname + modelName
    newfile   = pathFile +  layerName + ".shp"

    createMDO(gridLayer, newfile, layerName, name_fields, type_fields)
# ---------------------------
#
# --- Create a Reaction Layer
def createReactionLayer(gridLayer, pathFile, modelName, newname, nlay, nspec, ireact, isothm):

    newname = "reaction_layer_"
    name_fields = []
    type_fields = []

    for i in range(1,nlay+1):
        if isothm != 5 :
            name_fields.append('RHOB_'+ str(i) )
            type_fields.append(QVariant.Double)
        if isothm == 5 or isothm == 6:
            name_fields.append('PRSITY2_' + str(i))
            type_fields.append(QVariant.Double)

        for j in range(1,nspec +1):
            if isothm > 0:
                name_fields.append('SP1_' + str(i) + '_' + str(j) )
                type_fields.append(QVariant.Double)
                name_fields.append('SP2_' + str(i) + '_' +  str(j) )
                type_fields.append(QVariant.Double)

            if ireact > 0:
                name_fields.append('RC1_' + str(i) + '_' + str(j) )
                type_fields.append(QVariant.Double)

                name_fields.append('RC2_' + str(i) + '_' +  str(j) )
                type_fields.append(QVariant.Double)


    layerName = newname + modelName
    newfile   = pathFile +  layerName + ".shp"

    createMDO(gridLayer, newfile, layerName, name_fields, type_fields)
# ---------------------------

### --- Create a CHD Layer
##def createChdLayer(gridLayer, pathFile, modelName, nsp):
##
##    newname = "chd_layer_"
##    name_fields = []
##    type_fields = []
##
##    name_fields.append('from_lay')
##    type_fields.append(QVariant.Int)
##    name_fields.append('to_lay')
##    type_fields.append(QVariant.Int)
##
##    for i in range(1,nsp+1):
##        name_fields.append(str(i) + '_shead')
##        type_fields.append(QVariant.Double)
##
##        name_fields.append(str(i) + '_ehead')
##        type_fields.append(QVariant.Double)
##
##    layerName = newname + modelName
##    newfile   = pathFile +  layerName + ".shp"
##
##    createMDO(gridLayer, newfile, layerName, name_fields, type_fields)
### ---------------------------

# --- Create a GHB Layer
def createGhbLayer(gridLayer, pathFile, modelName, nsp, laynum):

    newname = "ghb_layer_"
    name_fields = []
    type_fields = []



    for i in range(1,nsp + 1):
        name_fields.append('from_lay_'+ str(i))
        type_fields.append(QVariant.Int)
        name_fields.append('to_lay_'+ str(i))
        type_fields.append(QVariant.Int)
        name_fields.append('bhead_' + str(i) )
        type_fields.append(QVariant.Double)
        name_fields.append('cond_' + str(i) )
        type_fields.append(QVariant.Double)
        name_fields.append('xyz_' + str(i) )
        type_fields.append(QVariant.Double)

    layerName = newname + modelName
    newfile   = pathFile +  layerName + ".shp"

    createMDO(gridLayer, newfile, layerName, name_fields, type_fields)
# ---------------------------