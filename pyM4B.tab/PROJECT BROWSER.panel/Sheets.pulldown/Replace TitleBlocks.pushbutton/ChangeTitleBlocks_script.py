# Author:	Giuseppe Dotto

__doc__ =	"Replace multiple TitleBlock with a single TypeBlock type."

from pyrevit import script, revit, DB
output = script.get_output()
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms
from rpw.ui.forms import SelectFromList


doc = revit.doc

BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter
tb_name = lambda t: t.Parameter[BIP.ELEM_FAMILY_AND_TYPE_PARAM].AsValueString()
tbType_name = lambda t: "{}: {}".format(t.FamilyName, t.Parameter[BIP.ALL_MODEL_TYPE_NAME].AsString())
sh_name = lambda s: s.SheetNumber + " - " + s.Name


collector = DB.FilteredElementCollector

# ASK FOR TITLEBLOCK TYPE
TitleBlocks_types = collector(doc).OfCategory(BIC.OST_TitleBlocks).WhereElementIsElementType().ToElements()
TitleBlocks_types = dict( [[tbType_name(t), t] for t in TitleBlocks_types] )
titleBlock_toPlace = SelectFromList("Change TitleBlocks", TitleBlocks_types,
					description="Select TitleBlock type to use.", sort=True)
if not titleBlock_toPlace:	script.exit()

# ASK FOR SHEETS WHERE TO USE SELECTED TITLEBLOCK
allSheets = collector(doc).OfCategory(BIC.OST_Sheets).WhereElementIsNotElementType()
allSheets = dict( [[sh_name(s), s] for s in allSheets] )

selected_sheets = forms.SelectFromList.show(sorted(allSheets.keys()),
				button_name = "Select Sheets where to change TitleBlocks",
				multiselect = True)
if not selected_sheets:	script.exit()
selected_sheets = [allSheets[n] for n in selected_sheets]

count = 0
with revit.Transaction("Change Titleblocks Type"):
	for sheet in selected_sheets:
		for tb in collector(doc, sheet.Id).OfCategory(BIC.OST_TitleBlocks).WhereElementIsNotElementType():
			tb.Parameter[BIP.ELEM_TYPE_PARAM].Set(titleBlock_toPlace.Id)
			count += 1

forms.alert("Sucessfully edit {} Titleblocks.".format(count), warn_icon=False)
