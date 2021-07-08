__author__ = 'Giuseppe Dotto'

__doc__ =	"Edit the Base Constraint parameter for all the selected walls, "\
			"modifying the Base Offset so that the wall position stays the same."\
			"\nInstruction: \n- Select the target Level."\
			"\n- Select the walls you want to edit."\

from pyrevit import revit, DB, UI
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms
from pyrevit import script

from Autodesk.Revit.UI.Selection import Selection


doc = revit.doc
uidoc = revit.uidoc
BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter

# ASK FOR LEVEL
lev = forms.select_levels(title='Select Levels', button_name='Select', width=500, multiple=False, filterfunc=None, doc=None, use_selection=False)

# SELECT THE WALL AND CHANGE PARAMETER
with revit.Transaction("edit Walls Base Constraint"):
	for wall in revit.get_picked_elements_by_category(BIC.OST_Walls, "Select walls to edit"):
		current_offset = wall.Parameter[BIP.WALL_BASE_OFFSET].AsDouble()
		current_level = wall.Parameter[BIP.WALL_BASE_CONSTRAINT].AsElementId()

		current_elevation = doc.GetElement(current_level).Elevation + current_offset
		future_offset = current_elevation - lev.Elevation


		# SET PARAMETERS
		wall.Parameter[BIP.WALL_BASE_CONSTRAINT].Set(lev.Id)
		wall.Parameter[BIP.WALL_BASE_OFFSET].Set(future_offset)


