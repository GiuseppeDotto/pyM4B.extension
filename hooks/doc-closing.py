
from pyrevit import revit, forms, HOST_APP
import os
import datetime

# import DB

doc = revit.doc
title = doc.Title

if 'ATA_SAN_' in title:
	directory_a = os.path.dirname(doc.PathName)

	deleted = 0
	deleted_name = []
	for dirpath, dirnames, filenames in os.walk(directory_a):
		for f in filenames:
			if '! - ' in f:
				deleted_name.append(f)
				full_name = os.path.join(dirpath, f)
				os.remove(full_name)
				deleted += 1
		break

	if deleted == 1:
		forms.alert( '{} file(s) deleted'.format(deleted), sub_msg=str(deleted_name), warn_icon=False )
	else:
		forms.alert( '{} file(s) deleted\nCOORDINATE WITH THE TEAM!'.format(deleted), sub_msg=str(deleted_name), warn_icon=True )
		
