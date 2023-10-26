
__title__ = "Grid Lines"

__doc__ =	"Make current the grids representation shorter by the input length."


from pyrevit import revit, DB, script
from pyrevit import PyRevitException, PyRevitIOError
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox,
							Separator, Button, CheckBox)

from pyrevit import forms
# import DB
doc = revit.doc
vw = doc.ActiveView
BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter


def unit_to_internal(doc, value):
	if int(doc.Application.VersionNumber) < 2022:
		um = doc.GetUnits().GetFormatOptions(DB.UnitType.UT_Length).DisplayUnits
		return	DB.UnitUtils.ConvertToInternalUnits(value, um)
	else:
		um = doc.GetUnits().GetFormatOptions(DB.SpecTypeId.Length).GetUnitTypeId()
		return	DB.UnitUtils.ConvertToInternalUnits(value, um)

def move_up(ln1, ln2):
	return	DB.Line.CreateBound(
		ln2.Project(ln1.GetEndPoint(0)).XYZPoint,
		ln2.Project(ln1.GetEndPoint(1)).XYZPoint)

def reduced_crv(crv, value):
	par = value/crv.Length
	return	DB.Line.CreateBound( crv.Evaluate(par, True), crv.Evaluate(1-par, True) )

# SELECT GRIDS
with forms.WarningBar(title='Pick Grids to edit'):
	grids = revit.pick_elements_by_category(BIC.OST_Grids)
if not grids:	script.exit()
views = forms.select_views()
if not views:	script.exit()


components = [Label('Grid reduction size:'),
			TextBox('value', '2000'),
			Separator(),
			Button('Select')]
form = FlexForm('Title', components)
form.show()
try: form.values['value']
except:
	forms.alert('Invalid number.', exitscript=True)
value = form.values['value']

value = unit_to_internal(doc, float(value))

with revit.Transaction('Reduce Grid extension by {}'.format(len(views))):
	d_type = DB.DatumExtentType.ViewSpecific
	for g in grids:
		for view in views:
			if g.Id in DB.FilteredElementCollector(doc,view.Id).OfCategory(BIC.OST_Grids).ToElementIds():
				crv = g.GetCurvesInView(d_type, view)[0]
				g.SetCurveInView(d_type, view, reduced_crv(crv, value))
