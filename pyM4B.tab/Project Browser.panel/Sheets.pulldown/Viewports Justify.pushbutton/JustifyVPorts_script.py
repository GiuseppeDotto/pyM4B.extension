# Author:	Giuseppe Dotto

__doc__ =	"Justify a set of viewports to the selected side."

from pyrevit import revit, DB, forms, script
from pyrevit import PyRevitException, PyRevitIOError


def average(numbers):
	return sum(numbers)/len(numbers)


BIC = DB.BuiltInCategory

# INPUT
selection = revit.get_selection()
if any(i.GetType() == DB.Viewport for i in selection):
	selected_viewports = [i for i in selection if i.GetType() == DB.Viewport]
else:
	selected_viewports = revit.pick_elements_by_category(BIC.OST_Viewports, 'Pick Viewports to align')

positions = ["Justify left", "Justify right", "Justify top", "Justify bottom", "Justify center X Axis", "Justify center Y Axis"]
pos = forms.CommandSwitchWindow.show(positions, message="Define type of justification")
if not pos:	script.exit()


# MOVE
with revit.Transaction("Viewports justication"):
	if pos == "Justify left":
		xs = [vp.GetBoxOutline().MinimumPoint.X for vp in selected_viewports]
		for vp in selected_viewports:
			delta = min(xs) - vp.GetBoxOutline().MinimumPoint.X
			vp.SetBoxCenter( vp.GetBoxCenter().Add(DB.XYZ(delta, 0,0)) )
			
	elif pos == "Justify right":
		xs = [vp.GetBoxOutline().MaximumPoint.X for vp in selected_viewports]
		for vp in selected_viewports:
			delta = max(xs) - vp.GetBoxOutline().MaximumPoint.X
			vp.SetBoxCenter( vp.GetBoxCenter().Add(DB.XYZ(delta, 0,0)) )
			
	elif pos == "Justify top":
		ys = [vp.GetBoxOutline().MaximumPoint.Y for vp in selected_viewports]
		for vp in selected_viewports:
			delta = max(ys) - vp.GetBoxOutline().MaximumPoint.Y
			vp.SetBoxCenter( vp.GetBoxCenter().Add(DB.XYZ(0, delta,0)) )
			
	elif pos == "Justify bottom":
		ys = [vp.GetBoxOutline().MinimumPoint.Y for vp in selected_viewports]
		for vp in selected_viewports:
			delta = min(ys) - vp.GetBoxOutline().MinimumPoint.Y
			vp.SetBoxCenter( vp.GetBoxCenter().Add(DB.XYZ(0, delta,0)) )

	elif pos == "Justify center X Axis":
		new_y = average([vp.GetBoxCenter().Y for vp in selected_viewports])
		for vp in selected_viewports:
			vp.SetBoxCenter( DB.XYZ(vp.GetBoxCenter().X, new_y, vp.GetBoxCenter().Z) )

	elif pos == "Justify center Y Axis":
		new_x = average([vp.GetBoxCenter().X for vp in selected_viewports])
		for vp in selected_viewports:
			vp.SetBoxCenter( DB.XYZ(new_x, vp.GetBoxCenter().Y, vp.GetBoxCenter().Z) )

