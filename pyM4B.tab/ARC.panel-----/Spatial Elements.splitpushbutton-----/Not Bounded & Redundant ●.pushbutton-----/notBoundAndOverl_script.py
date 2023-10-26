__author__ = "Giuseppe Dotto"
__doc__ =	"Returns the Not Bounded and Redoundant rooms visibe in the ACTIVE VIEW.\n\n"\
            "SHIFT-CLICK: Extend the analysis to all rhe Rooms in the project."

from pyrevit import revit, DB
from pyrevit import forms
from pyrevit import script

output = script.get_output()

SEBO = DB.SpatialElementBoundaryOptions()
def enclosed(r):
    BS = r.GetBoundarySegments(SEBO)
    return len(BS)>0

doc = revit.doc
BIC = DB.BuiltInCategory

if __shiftclick__:  
    allRooms = DB.FilteredElementCollector(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType()
else:
    vw = doc.ActiveView 
    allRooms = DB.FilteredElementCollector(doc, vw.Id).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType()

roomName = lambda r: r.Parameter[DB.BuiltInParameter.ROOM_NAME].AsString()
notPlaced = []
notEnclosed = []
redundant = []
totalRooms = 0
for r in allRooms:
	totalRooms += 1
	if r.Location == None:
		notPlaced.append(r)
	elif r.Area == 0:
		if enclosed(r): redundant.append(r)
		else:   notEnclosed.append(r)


space = "\n---------------\n\n"
if __shiftclick__:
	msg = "LIST OF ALL NOT ENCLOSED OR REDUNDANT ROOMS IN THE PROJECT."\
		"\ntotal number:\t{}\nnr of Not Placed:\t{}\nnr of Not Enclosed:\t{}\nnr of Redundant:\t{}"\
		.format(totalRooms, len(notPlaced), len(notEnclosed), len(redundant))\
		+"\nId (Level) Room Number - Room Name"
else:
	msg = "LIST OF ALL NOT ENCLOSED OR REDUNDANT ROOMS VISIBLE IN THE ACTIVE VIEW."\
		"\ntotal number:\t{}\nnr of Not Placed:\t{}\nnr of Not Enclosed:\t{}\nnr of Redundant:\t{}"\
		.format(totalRooms, len(notPlaced), len(notEnclosed), len(redundant))\
		+"\nId (Level) Room Number - Room Name"

msg += space + "NOT ENCLOSED:\n"
for elem in notEnclosed:
    msg += output.linkify(elem.Id) + " ({}) {} - {}\n".format(elem.Level.Name, elem.Number, roomName(elem))

msg += space + "REDUNDANT:\n"
for elem in redundant:
    msg += output.linkify(elem.Id) + " ({}) {} - {}\n".format(elem.Level.Name, elem.Number, roomName(elem))


print(msg)
