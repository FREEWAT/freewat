#-------------------------------------------------------------------------------
# Name:        modulo1
# Purpose:
#
# Author:      iacopo.borsi
#
# Created:     18/02/2015
# Copyright:   (c) iacopo.borsi 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from sqlite_utils import executeQuery

dbname = 'C:\Users\iacopo.borsi\Desktop\pluto.sqlite'
tableName = 'paperino'
fields = ('campo1','campo2')
params = (tableName, fields[0], fields[1]);
header,data= executeQuery('""CREATE TABLE "tbella" ( PKUID INTEGER PRIMARY KEY AUTOINCREMENT %s )""" ', fields ,  dbname)

executeQuery()


