
__doc__ = 'The tool is for automatically calculate the ration WindowArea/RoomArea'\
		" taking in consideration only the Curtain Wall Panels, Windows and Doors Types selected."\
		"\nIn addition, it gives the possibility to store the value in the room's selected parameter(s)"

from System.Collections.Generic import List
from pyrevit import script, revit, forms, DB
from rpw.ui.forms import FlexForm, Label, ComboBox, TextBox, Separator, Button
output = script.output.get_output()
# import DB

doc = revit.doc

# FUNCTION FOR COLLECTING WINDOWS/CWPL IN ROOMS
BIC = DB.BuiltInCategory
cat_fltr = DB.ElementMulticategoryFilter( List[BIC]([BIC.OST_Windows, BIC.OST_CurtainWallPanels, BIC.OST_Doors]) )
opt = DB.Options()
def is_in_room(r, wndw):
	bb = wndw.get_BoundingBox(None)
	pt = DB.Line.CreateBound(bb.Min, bb.Max).Evaluate(0.5, True)
	for m in [2, -2]:
		if r.IsPointInRoom(pt.Add(wndw.FacingOrientation.Multiply(m))):
			return True
	return False

def get_nearby(r, wndw_types):
	bb = r.get_BoundingBox(None)
	bb_flt = DB.BoundingBoxIntersectsFilter(DB.Outline(bb.Min, bb.Max), 3)
	wnwds = DB.FilteredElementCollector(doc).WherePasses(cat_fltr).WherePasses(bb_flt).WhereElementIsNotElementType()
	return [w for w in wnwds if w.GetTypeId() in wndw_types and is_in_room(r, w)] 

BIP = DB.BuiltInParameter
def area_formula(w):
	w = doc.GetElement(w.GetTypeId())
	width = max([w.get_Parameter(x).AsDouble() for x in [BIP.GENERIC_WIDTH, BIP.FAMILY_ROUGH_WIDTH_PARAM]])
	height = max([w.get_Parameter(x).AsDouble() for x in [BIP.GENERIC_HEIGHT, BIP.FAMILY_ROUGH_HEIGHT_PARAM]])
	return	width*height

def get_wndwArea(wndw):
	"""
	Return the area of the elements if it opens or comes from the give rooms
	"""
	if wndw.Category.Id == DB.Category.GetCategory(doc, BIC.OST_Windows).Id:
		# return  wndw.get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsDouble()/4
		return area_formula(wndw)
	else:
		return  wndw.get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsDouble()


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

# SELECT WINDOW TYPE USEFUL TO GENERATE AIR-LIGHT RATIO
wndw_types = DB.FilteredElementCollector(doc).WherePasses(cat_fltr).WhereElementIsNotElementType()
wndw_types = [doc.GetElement(w.GetTypeId()) for w in wndw_types]
wndw_types = dict( [['{} - {}: {}'.format(w.Category.Name, w.FamilyName, DB.Element.Name.__get__(w)), w] for w in wndw_types] )
selected = forms.SelectFromList.show(sorted(wndw_types.keys()),
									multiselect=True,
									button_name='Select Windows/CW Panels/Doors to consider')
forms.alert_ifnot(selected, 'No Windows/Curtain Panel selected.', exitscript=True)
wndw_types = [wndw_types[k].Id for k in selected]


# CALCULATE AIR-LIGHT RATIO
out = []
room_name = lambda r: r.Number + ': ' + r.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
for r in rooms:
	wndw_area = sum( [get_wndwArea(wndw) for wndw in get_nearby(r, wndw_types)] )
	wndw_area_sqm = DB.UnitUtils.ConvertFromInternalUnits(wndw_area, DB.UnitTypeId.SquareMeters)
	wndw_area_sqm = round(wndw_area_sqm, 2)
	if wndw_area > 0:
		value = round(wndw_area/r.Area, 3)
		out.append([room_name(r), wndw_area_sqm, value])
	else:
		out.append([room_name(r), wndw_area_sqm, '-'])

output.print_table(table_data=sorted(out), columns=['ROOM', 'WINDOWS AREA [sqm]', 'AIR-LIGHT RATIO'], title='OVERALL AIR-LIGHT RATIO')
print('\nThe AirLight ration should be at least equal to 1/8 ({}), or 1/10 ({}) in exceptional cases'.format(round(1.0/8, 3), round(1.0/10, 3)))

Y = True
y = True
if input('\n\nSET ROOMS PARAMETER WITH THE ABOVE VALUE? [Y/N]'):
	par_names = ['---'] + sorted([p.Definition.Name for p in r.Parameters])
	rooms = dict([[room_name(r), r] for r in rooms])
	components = [Label('total Windows Area'),
				  ComboBox('cb1', par_names),
				  Label('Air-Light Ratio'),
				  ComboBox('cb2', par_names),
				  Separator(),
				  Button('Select')]
	form = FlexForm('Title', components)
	form.show()

	with revit.Transaction('Set AirLight ratio - M4B'):
		if form.values['cb1'] and form.values['cb1'] != '---':
			for sub in out:
				rooms[sub[0]].LookupParameter(form.values['cb1']).Set( sub[1] )
		if form.values['cb2'] and form.values['cb2'] != '---':
			for sub in out:
				rooms[sub[0]].LookupParameter(form.values['cb2']).Set( sub[2] )
	
	print('\nDONE!')
	print('You can now close this window.')

else:
	print('not recognized input. Please type "Y" if you want to set the parameters.`')