# Author:	Giuseppe Dotto

__doc__ =	"Horizonatally justify a set of viewports."

from pyrevit import revit, DB
from pyrevit import PyRevitException, PyRevitIOError
# import DB


BIC = DB.BuiltInCategory

# INPUT
selected_viewports = revit.pick_elements_by_category(BIC.OST_Viewports, 'Pick Viewports to align')

# SORT VIEWPORTS
selected_viewports.sort(key=lambda v:v.GetBoxCenter().X)
total_span = selected_viewports[-1].GetBoxOutline().MaximumPoint.X\
			- selected_viewports[0].GetBoxOutline().MinimumPoint.X
v_width = lambda v: v.GetBoxOutline().MaximumPoint.X - v.GetBoxOutline().MinimumPoint.X

gap = (total_span-sum([v_width(v) for v in selected_viewports])) / (len(selected_viewports)-1)

new_positions = []
for n, v in enumerate(selected_viewports):
	if n == 0:
		new_positions.append(v.GetBoxCenter())
	else:
		new_x = new_positions[-1].X + v_width(selected_viewports[n-1])/2 + v_width(v)/2 + gap
		new_positions.append( DB.XYZ(new_x, v.GetBoxCenter().Y, v.GetBoxCenter().Z) )

# MOVE
with revit.Transaction("Viewports vertical justication"):
	for v, pt in zip(selected_viewports, new_positions):
		v.SetBoxCenter(pt)

