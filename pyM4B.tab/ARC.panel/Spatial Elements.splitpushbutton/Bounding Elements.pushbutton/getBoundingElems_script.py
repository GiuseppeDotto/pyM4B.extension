
__doc__ = "Return all the elements that are bounding the selected room."

from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script

output = script.get_output()

SEBO = DB.SpatialElementBoundaryOptions()
def get_listOfBounding(r):
	txt = ""
	ids = []
	for sub in r.GetBoundarySegments(SEBO):
		for bs in sub:
			i = bs.ElementId
			if i not in ids:
				ids.append(i)
				elem = doc.GetElement(i)
				if elem:
					txt += output.linkify(elem.Id) + '; {}; {}\n'.format(elem.Category.Name, elem.Name)
					# txt += '{};\t{}; {}\n'.format(elem.Id.IntegerValue, elem.Category.Name, elem.Name)
				else:
					txt += "None\n"
	return  txt

doc = revit.doc
BIC = DB.BuiltInCategory

getName = lambda r: r.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()

space = "\n---------------\n\n"

with forms.WarningBar(title='Select Rooms to analyse'):
	elems = revit.pick_elements_by_category(BIC.OST_Rooms)
if not elems:	script.exit()

print "LIST OF ALL THE SELECTED ROOMS AND THEIR BOUNDING ELEMENTS."\
	"\nRoom Number - Room Name\nId; Category; Name\n"
for r in elems:
	print(space + r.Number + " - " + getName(r) +\
			"\n\n" + get_listOfBounding(r))

