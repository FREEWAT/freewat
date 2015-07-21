#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Mutuated by QSpatiaLite plugin.

#-------------------------------------------------------------------------------
from PyQt4 import QtCore, QtGui
from qgis.core import *
from pyspatialite import dbapi2 as sqlite3

def pop_up_error(msg='',parent=None):
	"""Display an error message via Qt box"""
	QtGui.QMessageBox.warning(parent, 'error', '%s' % (msg))

def pop_up_info(msg='',parent=None,):
	"""Display an info message via Qt box"""
	QtGui.QMessageBox.information(parent, 'Information', '%s' % (msg))

def getQgisVectorLayers():
	"""Return list of all valid QgsVectorLayer in QgsMapLayerRegistry"""
	layermap = QgsMapLayerRegistry.instance().mapLayers()
	layerlist = []
	for name, layer in layermap.iteritems():
		if layer.isValid() and layer.type() == QgsMapLayer.VectorLayer:
				layerlist.append( layer )
	return layerlist

##def loadInQGIS_spatial(parent,db, query,geocol,tablename=''):
##	"""Load query to QGIS Canvas (spatial layers)"""
##	if tablename == '':
##		tablename = 'SQLresult'
##	#Prepare URI()
##	uri = QgsDataSourceURI()
##	uri.setDatabase(db.path)
##	uri.setDataSource('', "(%s)" %query, "%s"%geocol, '',"ROWID")
##	layer=QgsVectorLayer(uri.uri(), tablename, 'spatialite')
##	#Test layer validity
##	if not layer.isValid():
##		pop_up_error("The result can't be Loaded into QGIS. Remember to alias your columns according to the name asked in the 'Geometry field'",parent)
##		return False
##	QgsMapLayerRegistry.instance().addMapLayer(layer)
##	return True


def uploadQgisVectorLayer(dbName, layer, tableName  , srid=None, selected=False, mapinfo=True):
    """Upload layer (QgsMapLayer) (optionnaly only selected values ) into current DB, in tableName (string) with desired SRID (default layer srid if None) - user can desactivate mapinfo compatibility Date importation. Return True if operation succesfull or false in all other cases"""

    # Connect to DB
    # creating/connecting SQL database object
    con = sqlite3.connect(dbName)

    # con = sqlite3.connect(":memory:") if you want write it in RAM
    con.enable_load_extension(True)
    cur = con.cursor()
    # Initialise spatial db
    # Insert a control for existing table or not
    cur.execute("PRAGMA foreign_keys = ON")
    # cur.execute("SELECT load_extension('libspatialite.so.5');")
    # Initializing Spatial MetaData: GEOMETRY_COLUMNS and SPATIAL_REF_SYS
    cur.execute("SELECT InitSpatialMetaData(1);")

    # --
    selected_ids=[]
    if selected==True :
        if layer.selectedFeatureCount()==0:
    	   pop_up_info("No selected item in Qgis layer: %s)"%layer.name())
    	   return False
    select_ids=layer.selectedFeaturesIds()

    #Get data charset
    provider=layer.dataProvider()
    #charset=provider.encoding()

    #Get fields with corresponding types
    fields=[]
    fieldsNames=[]
    mapinfoDAte=[]
    for id,name in enumerate(provider.fields().toList()):
        fldName=unicode(name.name()).replace("'"," ").replace('"'," ")
        #Avoid two cols with same name:
        while fldName.upper() in fieldsNames:
    	   fldName='%s_2'%fldName
        fldType=name.type()
        fldTypeName=unicode(name.typeName()).upper()
        if fldTypeName=='DATE' and unicode(provider.storageType()).lower()==u'mapinfo file'and mapinfo==True: # Mapinfo DATE compatibility
    	   fldType='DATE'
    	   mapinfoDAte.append([id,fldName]) #stock id and name of DATE field for MAPINFO layers
        elif fldType in (QtCore.QVariant.Char,QtCore.QVariant.String): # field type is TEXT
            fldLength=name.length()
            fldType='TEXT(%s)'%fldLength  #Add field Length Information
        elif fldType in (QtCore.QVariant.Bool,QtCore.QVariant.Int,QtCore.QVariant.LongLong,QtCore.QVariant.UInt,QtCore.QVariant.ULongLong): # field type is INTEGER
    	   fldType='INTEGER'
        elif fldType==QtCore.QVariant.Double: # field type is DOUBLE
    	   fldType='REAL'
        else: # field type is not recognized by SQLITE
    	   fldType=fldTypeName
        fields.append(""" "%s" %s """%(fldName,fldType))
        fieldsNames.append(fldName.upper())

    # is it a geometric table ?
    geometry=False
    if layer.hasGeometryType():
        #Get geometry type
        geom=['MULTIPOINT','MULTILINESTRING','MULTIPOLYGON','UnknownGeometry']
        geometry=geom[layer.geometryType()]
        #Project to new SRID if specified by user:
    if srid==None:
    	srid=layer.crs().postgisSrid()
    else:
    	Qsrid = QgsCoordinateReferenceSystem()
    	Qsrid.createFromId(srid)
    	if not Qsrid.isValid(): #check if crs is ok
    		pop_up_error("Destination SRID isn't valid for table %s"%layer.name(),self.parent)
    		return False
    	layer.setCrs(Qsrid)

    #select attributes to import (remove Pkuid if already exists):
    allAttrs = provider.attributeIndexes()
    fldDesc = provider.fieldNameIndex("PKUID")
    if fldDesc != -1:
        print "Pkuid already exists and will be replaced!"
        del allAttrs[fldDesc] #remove pkuid Field
        del fields[fldDesc] #remove pkuid Field
        #provider.select(allAttrs)
        #request=QgsFeatureRequest()
        #request.setSubsetOfAttributes(allAttrs).setFlags(QgsFeatureRequest.SubsetOfAttributes)

    if geometry:
        fields.insert(0,"Geometry %s"%geometry)

    #Create new table in DB
        fields=','.join(fields)
        if len(fields)>0:
            fields=', %s'%fields
            cur.execute("""CREATE TABLE "%s" ( PKUID INTEGER PRIMARY KEY AUTOINCREMENT %s )"""%(tableName, fields))


    #Recover Geometry Column:
    if geometry:
        cur.execute("""SELECT RecoverGeometryColumn("%s",'Geometry',%s,'%s',2)"""%(tableName,srid,geometry,))

	# Retreive every feature
	for feat in layer.getFeatures():
		# selected features:
		if selected and feat.id()not in select_ids:
			continue

		#PKUID and Geometry
		values_auto=['NULL'] #PKUID value
		if geometry:
			geom = feat.geometry()
			#WKB=geom.asWkb()
			WKT=geom.exportToWkt()
			values_auto.append('CastToMulti(GeomFromText("%s",%s))'%(WKT,srid))

		# show all attributes and their values
		values_perso=[]
		for val in allAttrs: # All except PKUID
			values_perso.append(feat[val])

		#Create line in DB table
		if len(fields)>0:
			cur.execute("""INSERT INTO "%s" VALUES (%s,%s)"""%(tableName,','.join([unicode(value).encode('utf-8') for value in values_auto]),','.join('?'*len(values_perso))),tuple([unicode(value) for value in values_perso]))
		else: #no attribute Datas
			cur.execute("""INSERT INTO "%s" VALUES (%s)"""%(table_name,','.join([unicode(value).encode('utf-8') for value in values_auto])))



    for date in mapinfoDAte: #mapinfo compatibility: convert date in SQLITE format (2010/02/11 -> 2010-02-11 ) or rollback if any error
        cur.execute("""UPDATE OR ROLLBACK "%s" set '%s'=replace( "%s", '/' , '-' )  """%(tableName,date[1],date[1]))

    # Close SpatiaLiteDB
    cur.close()
    # Save the changes
    con.commit()
    # Close connection
    con.close()
    return True


def getTableNamesList(db):
    # Connect to DB
    # creating/connecting SQL database object
    con = sqlite3.connect(db)

    # select all tables name from DB
    query = " SELECT name FROM sqlite_master WHERE type = 'table' "

    cur = con.cursor()
    rs = cur.execute( query )
    data = [row for row in cur]
    namesList = []
    for k in range(len(data)):
        namesList.append( data[k][0].encode( 'mbcs'))

    # Close SpatiaLiteDB
    cur.close()
    # Close connection
    con.close()

    return namesList


def checkIfTableExists(db,targetname, popupExists = False, popupNoExists = False):
    check = False

    namelist = getTableNamesList(db)
    for name in namelist:
        if name == targetname:
            check = True
    if check == True & popupExists == True:
        msg = 'Table %s already exists in DB'%targetname
        QtGui.QMessageBox.information(None, 'Warning', '%s' % (msg))
    if check == False & popupNoExists == True:
        msg2 = 'Table %s does not exist in DB'%targetname
        QtGui.QMessageBox.information(None, 'Warning', '%s' % (msg2))

    return check

