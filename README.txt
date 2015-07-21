
---
freewat_utils
Methods used in several modules

---
sqlite_utils
Methods used in several modules for connection to/from DB Spatialite

---
mdo_utils
It contains all methods to create Model, DB, MDOs and other usuful stuff 

---
UIs are stored within /ui folder

-- ************* ---
DEPENDENCIES
---
Flopy Version 3 has to be installed.
In turn, dependencies needed by Flopy are listed at Flopy web site: 
https://github.com/modflowpy/flopy/blob/master/readme.md 

To install flopy:
1. Flopy package can be installed through PIP. If you don't have, PIP you can do it following:
https://pip.pypa.io/en/latest/installing.html 
You should first download get-pip.py in your local folder and from then: 
python get-pip.py

2. Once PIP has installed, you can install flopy:
pip install flopy
The latest version of flopy will be installed.
If you experience some problem (especially under QGIS) you can force the installation to a former version.
The following should work, for instance, with QGIS 2.8 under Windows 7:

pip install flopy==3.0.1

