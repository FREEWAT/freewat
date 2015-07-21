# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Freewat
                                 A QGIS plugin
 Build and Run MODFLOW models
                             -------------------
        begin                : 2015-01-06
        copyright            : (C) 2015 by Iacopo Borsi TEA Sistemi
        email                : iac
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Freewat class from file Freewat.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from Freewat import Freewat
    return Freewat(iface)
