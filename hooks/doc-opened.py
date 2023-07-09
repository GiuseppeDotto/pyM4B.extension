
from pyrevit import revit, forms, HOST_APP
import os
import datetime

# import DB

doc = revit.doc
title = doc.Title

if 'ATA_SAN_' in title:
	u_name = HOST_APP.username

	name = '! - {} - {} - {}.txt'.format(title, u_name, datetime.datetime.today().strftime('%y%m%d %H-%M-%S'))

	directory_a = os.path.dirname(doc.PathName)
	directory_b = os.path.dirname(__file__ )


	# CHECK YOU ARE THE ONLY ONE
	for dirpath, dirnames, filenames in os.walk(directory_a):
		for f in filenames:
			if '! - '+title in f:
				forms.alert('CLOSE THE FILE!\nANOTHER USER HAS IT OPEN.', warn_icon=True, exitscript=True)
		break

	# CREATE TEMPORARY FILE
	full_name = os.path.join(directory_a, name)
	fp = open(full_name, 'w')
	fp.close()

	forms.alert('1 file created in project folder.', sub_msg=full_name, warn_icon=False )
