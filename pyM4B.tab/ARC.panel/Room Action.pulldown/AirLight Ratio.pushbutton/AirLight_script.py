
__doc__ = 'The tool is for automatically calculate the ration RoomArea/WindowArea'\
        " taking in consideration also the Curtain Wall Panels and storing the value in the room's selected parameter"

from System.Collections.Generic import List
from pyrevit import script, revit, forms, DB
output = script.output.get_output()
# import DB

doc = revit.doc

# FUNCTION FOR COLLECTING WINDOWS/CWPL IN ROOMS
BIC = DB.BuiltInCategory
cat_fltr = DB.ElementMulticategoryFilter( List[BIC]([BIC.OST_Windows, BIC.OST_CurtainWallPanels]) )
def get_nearby(r):
    bb = r.get_BoundingBox(None)
    bb_flt = DB.BoundingBoxIntersectsFilter( DB.Outline(bb.Min, bb.Max), 3 )
    return  DB.FilteredElementCollector(doc).WherePasses(cat_fltr).WherePasses(bb_flt).WhereElementIsNotElementType()

def get_wndwArea(r, wndw):
    """
    Return the area of the elements if it opens or comes from the give rooms
    """
    bb = wndw.get_BoundingBox(None)
    pt = DB.Line.CreateBound(bb.Min, bb.Max).Evaluate(0.5, True)
    for m in [2, -2]:
        if r.IsPointInRoom(pt.Add(wndw.FacingOrientation.Multiply(m))):
            return  wndw.get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsDouble()
    return 0    


# SELECT ROOMS
rooms = forms.CommandSwitchWindow.show(['All Rooms', 'Rooms in Active View', 'Pick Rooms'], title='Choose the Rooms to analyze')
if rooms == 'All Rooms':
    rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    rooms = [r for r in rooms if r.Area]
elif rooms == 'Rooms in Active View':
    rooms = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
    rooms = [r for r in rooms if r.Area]
else:
    rooms = revit.pick_elements_by_category(DB.BuiltInCategory.OST_Rooms, 'Pick Rooms to analyze')
forms.alert_ifnot(rooms, 'No Rooms selected.', exitscript=True)

# CALCULATE AIR-LIGHT RATIO
out = []
room_name = lambda r: r.Number + ': ' + r.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
for r in rooms:
    wndw_area = sum( [get_wndwArea(r, wndw) for wndw in get_nearby(r)] )
    if wndw_area > 0:
        value = round(wndw_area/r.Area, 2)
        out.append([room_name(r), value])
    else:
        out.append([room_name(r), '-'])

output.print_table(table_data=sorted(out), columns=['ROOM', 'AIR-LIGHT RATIO'], title='OVERALL AIR-LIGHT RATIO')


