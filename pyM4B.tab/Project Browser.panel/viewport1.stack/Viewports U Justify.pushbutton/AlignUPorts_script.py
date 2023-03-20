# Author:	Giuseppe Dotto

__doc__ =	"Horizonatally justify a set of viewports."

from pyrevit import revit, DB
from pyrevit import PyRevitException, PyRevitIOError


def double_range(start, end, nr):
	increment = (float(end)-start) / (nr-1)
	for n in range(nr):
		yield start + increment*n


BIC = DB.BuiltInCategory

# INPUT
selected_viewports = revit.pick_elements_by_category(BIC.OST_Viewports, 'Pick Viewports to align')

# SORT VIEWPORTS
sorted_viewports = sorted([[vp.GetBoxCenter().X, vp] for vp in selected_viewports])
sorted_viewports = zip(*sorted_viewports)

xs = sorted_viewports[0]
viewports = sorted_viewports[1]

# MOVE
with revit.Transaction("Viewports vertical justication"):
	for vp, new_x in zip(viewports, double_range(xs[0], xs[-1], len(xs))):
		vp.SetBoxCenter( DB.XYZ(new_x, vp.GetBoxCenter().Y, vp.GetBoxCenter().Z) )

