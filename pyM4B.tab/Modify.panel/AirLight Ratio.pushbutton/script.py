
from pyrevit import DB, revit, forms, script
from rpw.ui.forms import FlexForm, Label, ComboBox, TextBox, Separator, Button, CheckBox
from System.Collections.Generic import List # type: ignore
try: import DB
except: pass

# Global variables
output = script.get_output()
doc = revit.doc
uidoc = revit.uidoc
BIC = DB.BuiltInCategory

# Create phase filter
phases = DB.FilteredElementCollector(doc).OfClass(DB.Phase)
phases = dict([[p.Name, p] for p in phases])
phase = forms.CommandSwitchWindow.show(phases, message='Select Phase')
phase = phases.get(phase)
if not phase: script.exit()
phase_filter = DB.ElementPhaseStatusFilter(phase.Id,
                                           List[DB.ElementOnPhaseStatus]([DB.ElementOnPhaseStatus.New,
                                                                          DB.ElementOnPhaseStatus.Existing]),
                                           False)

# Custom Functions
all_rooms = DB.FilteredElementCollector(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType()
all_rooms = [r for r in all_rooms if r.get_Parameter(DB.BuiltInParameter.ROOM_PHASE).AsElementId() == phase.Id]
forms.alert_ifnot(len(all_rooms) > 0, 
                  'no rooms found in the projects', 
                  exitscript=True)

def get_adjacentRooms(e, all_rooms=all_rooms):
    bb = e.get_BoundingBox(None)
    pt = DB.Line.CreateBound(bb.Min, bb.Max)
    pt = pt.Evaluate(0.5, True)
    if hasattr(e, 'FacingOrientation'):
        pt1 = pt.Add(e.FacingOrientation.Multiply(2))
        pt2 = pt.Add(e.FacingOrientation.Multiply(-2))
    elif hasattr(e, 'Orientation'):
        pt1 = pt.Add(e.Orientation.Multiply(2))
        pt2 = pt.Add(e.Orientation.Multiply(-2))
    else: return None
    out = []
    for r in all_rooms:
        if r.IsPointInRoom(pt1):    out.append(r.Id)
        if r.IsPointInRoom(pt2):    out.append(r.Id)
        if len(out) == 2:   break
    return out

def get_parameterNames(bic, specType=DB.SpecTypeId.Area):
    elems = DB.FilteredElementCollector(doc).OfCategory(bic).WhereElementIsNotElementType().WherePasses(phase_filter)
    temp = set()
    for w in elems:
        for p in w.Parameters:
            if p.StorageType == DB.StorageType.Double and p.Definition.GetDataType() == specType:
                temp.add('[instance] '+p.Definition.Name)
        for p in doc.GetElement(w.GetTypeId()).Parameters:
            if p.StorageType == DB.StorageType.Double and p.Definition.GetDataType() == specType:
                temp.add('[type] '+p.Definition.Name)
    return list(temp)

room_name = lambda r: DB.Element.Name.__get__(r)


# DEFINE USER INPUTS
# room_parameters = [p.Definition.Name for p in all_rooms[0].Parameters if p.StorageType == DB.StorageType.Double]
room_parameters_area = [p.Definition.Name for p in all_rooms[0].Parameters if p.Definition.GetDataType() == DB.SpecTypeId.Area and not p.IsReadOnly]
room_parameters_ratio = [p.Definition.Name for p in all_rooms[0].Parameters if p.Definition.GetDataType() == DB.SpecTypeId.Number and not p.IsReadOnly]
components = [Label('ROOMS PARAMETERS TO SET'),
              Label('Ratio:'),
              ComboBox('ratio', ['---']+room_parameters_ratio),
              Label('Total Vertical Area:'),
              ComboBox('vArea', ['---']+room_parameters_area),
              Separator(),
              Label('ELEMENTS PARAMETERS TO READ'),
              Label('Windows:'),
              ComboBox('Window', ['---']+get_parameterNames(BIC.OST_Windows)),
              Label('Doors:'),
              ComboBox('Door', ['---']+get_parameterNames(BIC.OST_Doors)),
              Label('Curatin Wall Panels:'),
              ComboBox('CurtainWallPanel', ['---']+get_parameterNames(BIC.OST_CurtainWallPanels)),
              Separator(),
              Button('Select')]
custom_params = FlexForm('AirLight Ratio User Input', components)
custom_params.show()
custom_params = custom_params.values
if not custom_params.get('ratio'):
    uidoc.RefreshActiveView()
    script.exit()

par_ratio_to_set = custom_params.pop('ratio')
par_area_to_set = custom_params.pop('vArea')
if '---' in [par_ratio_to_set, par_area_to_set]:
    forms.alert('no parameter for "Ratio" or "Total Vertical Area" selected.', exitscript=True)
custom_params['Window'] = [BIC.OST_Windows, custom_params['Window']]
custom_params['Door'] = [BIC.OST_Doors, custom_params['Door']]
custom_params['CurtainWallPanel'] = [BIC.OST_CurtainWallPanels, custom_params['CurtainWallPanel']]

# create filter 1
multicat = [BIC.OST_Windows, BIC.OST_Doors, BIC.OST_CurtainWallPanels]
multicat = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory](multicat))
to_select = []
data = []
result = []
par_set = 0
with revit.Transaction('M4B - AirLight Ratio'):
    for room in all_rooms:
        # create filter 2
        bb = room.get_BoundingBox(None)
        filter2 = DB.BoundingBoxIntersectsFilter(DB.Outline(bb.Min, bb.Max), 3)

        # get all interesting openings
        openings = DB.FilteredElementCollector(doc).WherePasses(phase_filter)\
                                                   .WherePasses(multicat)\
                                                   .WherePasses(filter2)
        total_area = 0.0
        for i in openings:
            adjacent_rooms = get_adjacentRooms(i)
            if len(adjacent_rooms) == 1 and adjacent_rooms[0] == room.Id:
                to_select.append(i.Id)
                for k in custom_params.keys():
                    if i.Category.Id == DB.Category.GetCategory(doc, custom_params[k][0]).Id and custom_params[k][1]:
                        par = None
                        par_name = custom_params[k][1]
                        if '[instance] ' in par_name:
                            par = i.LookupParameter(par_name.replace('[instance] ', ''))
                        elif '[type] ' in par_name:
                            par = doc.GetElement(i.GetTypeId()).LookupParameter(par_name.replace('[type] ', ''))
                        if par:
                            total_area += par.AsDouble()
                            data.append([room_name(room),
                                         '[{}] {}'.format(i.Id.ToString(),
                                                          i.get_Parameter(DB.BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM).AsValueString()),
                                          DB.UnitUtils.ConvertFromInternalUnits(par.AsDouble(), par.GetUnitTypeId())])

        par = room.get_Parameter(DB.BuiltInParameter.ROOM_AREA)
        ratio = total_area/par.AsDouble()
        result.append([room_name(room), 
                    DB.UnitUtils.ConvertFromInternalUnits(total_area, par.GetUnitTypeId()),
                    DB.UnitUtils.ConvertFromInternalUnits(par.AsDouble(), par.GetUnitTypeId()),
                    ratio])
        if par_ratio_to_set:
            par_set += 1
            room.LookupParameter(par_ratio_to_set).Set(ratio)
            room.LookupParameter(par_area_to_set).Set(total_area)

uidoc.RefreshActiveView()
uidoc.Selection.SetElementIds(List[DB.ElementId](to_select))

export = forms.alert('{} Rooms update'.format(par_set), 
                     warn_icon=False,
                     options=['Export data to CSV', 'Close'])

if export == 'Export data to CSV':
    # export CSV
    import csv
    file_path = forms.save_file(file_ext='csv')
    if file_path:
        with open(file_path.replace('.csv', ' - summary.csv'), 'wb') as file:
            writer = csv.writer(file)
            writer.writerows( [['Room', 'Openings', 'Floor', 'Ratio']]+result )
        with open(file_path.replace('.csv', ' - detail.csv'), 'wb') as file:
            writer = csv.writer(file)
            writer.writerows( [['Room', 'Family Instance', 'Area']]+data )
