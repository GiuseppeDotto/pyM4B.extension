
__doc__ = "Move the room tags to the center of the room."

from pyrevit import revit, DB
from pyrevit import forms

doc = revit.doc
uidoc = revit.uidoc
vw = doc.ActiveView
BIC = DB.BuiltInCategory


# UI CHOOSE THE OPTION
context = ['All tags in active view',
		'All tags in active view but the ones with leader',
		'Select Tags']
user_input = forms.CommandSwitchWindow.show(context)


# SELECT TAG
if user_input:
	if user_input == context[0]:
		tags = DB.FilteredElementCollector(doc, vw.Id).OfCategory(BIC.OST_RoomTags).WhereElementIsNotElementType()
	elif user_input == context[1]:
		tags = DB.FilteredElementCollector(doc, vw.Id).OfCategory(BIC.OST_RoomTags).WhereElementIsNotElementType()
		tags = [i for i in tags if not i.HasLeader]
	elif user_input == context[2]:
		with forms.WarningBar(title='Pick room tags to centralize'):
			tags = revit.pick_elements_by_category(BIC.OST_RoomTags)

	# MOVE TAGS
	with revit.Transaction('Centralize Room Tags'):
		for t in tags:
			t.Location.Point = t.Room.Location.Point

	uidoc.RefreshActiveView()

