# Author:	Giuseppe Dotto

__doc__ =	"Delete multiple sheets at a time, selecting them through their name."

from pyrevit import revit, DB, UI, script
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms

doc = revit.doc

toDel = forms.select_sheets()

if not toDel:	script.exit()
if forms.alert("delete {} Sheets?".format(len(toDel)), yes = True, no = True):
	activeVwId = doc.ActiveView.Id
	with revit.Transaction("{} Sheets deleted".format(len(toDel))):
		for vw in toDel:
			if vw.IsValidObject:
				if vw.Id == activeVwId:
					forms.alert("Active view can't be deleted.")
				else:
					doc.Delete(vw.Id)

