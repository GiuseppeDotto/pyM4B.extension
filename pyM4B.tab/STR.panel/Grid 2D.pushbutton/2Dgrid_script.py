# Author:	Giuseppe Dotto

__doc__ =	"Change Grids display to 2D in active view."

from pyrevit import revit, DB
from pyrevit import PyRevitException, PyRevitIOError

from pyrevit import forms

def new_line(ln):
	return	DB.Line.CreateBound(ln.Evaluate(0.00005, True), ln.Evaluate(0.99999, True))

doc = revit.doc
active_view = doc.ActiveView

BIC = DB.BuiltInCategory

with forms.ProgressBar(title='Select Grids to transform to 2D'):
	grids = revit.pick_elements_by_category(BIC.OST_Grids, 'Select Grids to transform')
if not grids:	grids = []

viewSpecific = DB.DatumExtentType.ViewSpecific

edit = 0
with revit.Transaction('Grids to 2D'):
	for g in grids:
		crv = g.GetCurvesInView(viewSpecific, active_view)
		if len(crv) == 1:
			g.SetCurveInView(viewSpecific, active_view, new_line(crv[0]))
			edit += 1

forms.alert('{} Grids converted to 2D.'.format(edit), warn_icon=False)
