
from pyrevit import revit, forms, HOST_APP
import os
import datetime

import DB

doc = revit.doc
title = doc.Title

if 'ATA_SAN_' in title:
	u_name = HOST_APP.username

	name = '{} - {}.txt'.format(u_name,  datetime.datetime.today())

	directory_a = doc.PathName
	directory_b = os.path.pardir( __file__ )

	msg = '{}\n{}\n{}'.format(title, name, directory_a, directory_b)

	forms.alert( msg, warn_icon=False )
