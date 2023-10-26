
__doc__ = "Move the room placement point and its tags to the center of its geometry. "\
		"It might works differently for not rectangular rooms."

import math
from pyrevit import script, revit, DB
from pyrevit import forms

doc = revit.doc
uidoc = revit.uidoc
BIC = DB.BuiltInCategory

def float_range(start, end, nr):
	nr = int(nr)
	increment = float(end-start)/int(nr-1)
	for i in range(nr):
		yield	start + increment*i

def get_centerPoint(room):
	bb = room.get_BoundingBox(None)
	pt = DB.Line.CreateBound(bb.Min, bb.Max).Evaluate(0.5, True)
	if room.IsPointInRoom(pt):
		return	pt
	else:
		ratio = math.fabs(bb.Min.Y-bb.Max.Y) / math.fabs(bb.Min.X-bb.Max.X)
		for divisions in range(5, 10):
			xs = list(float_range(bb.Min.X, bb.Max.X, divisions))
			ys = list(float_range(bb.Min.Y, bb.Max.Y, divisions*ratio))
			for x in xs[1:-1]:
				for y in ys[1:-1]:
					pt = DB.XYZ(x, y, pt.Z)
					if room.IsPointInRoom(pt):	
						return	pt

tag_cat = DB.Category.GetCategory(doc, BIC.OST_RoomTags).Id
def center_tag(room):
	for i in room.GetDependentElements(None):
		elem = doc.GetElement(i)
		if elem.Category and elem.Category.Id == tag_cat:
			elem.Location.Point = room.Location.Point

# SELECT ROOMS
context = ['Manually select', 'All in acrive view', 'All in project']
ui = forms.CommandSwitchWindow.show(context)
if ui == context[0]:
	with forms.WarningBar(title='Pick rooms to centralize'):
		rooms = revit.pick_elements_by_category(BIC.OST_Rooms)
elif ui == context[1]:
	rooms = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType()
elif ui == context[2]:
	rooms = DB.FilteredElementCollector(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType()


# MOVE LOCATION POINTS
if rooms:
	with revit.Transaction('Centralize Rooms'):
		for room in rooms:
			if get_centerPoint(room):
				room.Location.Point = get_centerPoint(room)
				center_tag(room)

uidoc.RefreshActiveView()

