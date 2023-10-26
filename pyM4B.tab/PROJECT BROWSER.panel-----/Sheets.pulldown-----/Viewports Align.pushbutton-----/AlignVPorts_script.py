# Author:	Giuseppe Dotto

__doc__ =	"Aligning a set of viewports to a single one.\n\n"\
			"Instructions:\nfrom the first form select the reference viewport, "\
			"from the second form select the viewports to align. "\
			"Finally define the type alignement between viewports.\n\n"\
			"The viewport name in the forms are be displayed as:\n 'SheetNumber - SheetName : ViewName'"

from pyrevit import revit, DB, UI, script
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms


def XYZvec(pt1, pt2):
	#return	XYZ(pt1.X-pt2.X, pt1.Y-pt2.Y, pt1.Z-pt2.Z)
	return	pt1.Subtract(pt2)


def	getKey(v):
	sh = doc.GetElement(v.SheetId)
	vw = doc.GetElement(v.ViewId)
	nm = sh.SheetNumber + " - " + sh.Name + " : " + vw.Name
	return	nm


doc = revit.doc

BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter

collector = DB.FilteredElementCollector
allViewports = collector(doc).OfCategory(BIC.OST_Viewports).WhereElementIsNotElementType()
allKey = [getKey(v) for v in allViewports]

_dict_ = dict(zip(allKey, allViewports))

# INPUT
viewFrom = forms.SelectFromList.show(sorted(allKey), title = "select reference viewport", multiselect=False, button_name='Select reference ViewPort')
if not viewFrom:	script.exit()
else:	viewFrom = _dict_[viewFrom]
viewportsToMove = forms.SelectFromList.show(sorted(allKey), title = "select viewports to align", multiselect=True, button_name='Select ViewPorts to align')
if not viewportsToMove:	script.exit()
else:	viewportsToMove = [_dict_[x] for x in viewportsToMove]

positions = ["Center", "Top left", "Top right", "Bottom left", "Bottom right"]
pos = forms.CommandSwitchWindow.show(positions, message="Define alignement point")
if not pos:	script.exit()


# MOVE
with revit.Transaction("Align Viewports"):
	for viewTo in viewportsToMove:
		if pos == "Center":
			viewTo.SetBoxCenter(viewFrom.GetBoxCenter())
		elif pos == "Bottom left":
			vec = viewFrom.GetBoxOutline().MinimumPoint.Subtract( viewTo.GetBoxOutline().MinimumPoint )
			viewTo.SetBoxCenter(viewTo.GetBoxCenter().Add(vec))
		elif pos == "Top right":
			vec = viewFrom.GetBoxOutline().MaximumPoint.Subtract( viewTo.GetBoxOutline().MaximumPoint )
			viewTo.SetBoxCenter(viewTo.GetBoxCenter().Add(vec))
			
		elif pos == "Bottom right":
			pt1 = DB.XYZ(viewTo.GetBoxOutline().MaximumPoint.X, viewTo.GetBoxOutline().MinimumPoint.Y,0)
			pt2 = DB.XYZ(viewFrom.GetBoxOutline().MaximumPoint.X, viewFrom.GetBoxOutline().MinimumPoint.Y,0)
			vec = pt2.Subtract(pt1)
			viewTo.SetBoxCenter(viewTo.GetBoxCenter().Add(vec))
		elif pos == "Top left":
			pt1 = DB.XYZ(viewTo.GetBoxOutline().MinimumPoint.X, viewTo.GetBoxOutline().MaximumPoint.Y,0)
			pt2 = DB.XYZ(viewFrom.GetBoxOutline().MinimumPoint.X, viewFrom.GetBoxOutline().MaximumPoint.Y,0)
			vec = pt2.Subtract(pt1)
			viewTo.SetBoxCenter(viewTo.GetBoxCenter().Add(vec))
