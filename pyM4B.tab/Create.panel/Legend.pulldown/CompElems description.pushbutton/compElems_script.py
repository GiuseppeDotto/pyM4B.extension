
__doc__ = "This function collect all the used type walls in the project "\
		"and fill a give multi-line text with information about its layer coposition."\
			"Returning with and material name."

from pyrevit import script, revit, DB, forms
# import DB

doc = revit.doc
BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter

def get_layers(w_type):
	"""
	INPUT: wall type\n
	OUTPUT: [all_widths, material_ids]
	"""
	all_width = []
	materials_id = []
	if w_type.GetCompoundStructure():
		for l in reversed(w_type.GetCompoundStructure().GetLayers()):
			if l.Width: 
				all_width.append( l.Width )
				materials_id.append( l.MaterialId )
	return all_width, materials_id

def used_and_unused_types(builtincategory):
	elems = DB.FilteredElementCollector(doc).OfCategory(builtincategory).WhereElementIsNotElementType()
	e_types_used = set( [e.GetTypeId() for e in elems] )
	e_types_unused = DB.FilteredElementCollector(doc).OfCategory(builtincategory).WhereElementIsElementType().ToElementIds()
	e_types_unused = set(e_types_unused) - e_types_used
	e_types_used = [doc.GetElement(i) for i in e_types_used]
	e_types_unused = [doc.GetElement(i) for i in e_types_unused]
	all_e_types = dict( [['( used ) '+e.get_Parameter(BIP.ALL_MODEL_TYPE_NAME).AsString(), e] for e in e_types_used] )
	for e in e_types_unused:	all_e_types['(unused) '+e.get_Parameter(BIP.ALL_MODEL_TYPE_NAME).AsString()] = e
	return  all_e_types

category = forms.CommandSwitchWindow.show(['Ceilings', 'Floors', 'Walls', 'Roofs'])
if not category:    script.exit()

if category == 'Ceilings': b_cat = BIC.OST_Ceilings
elif category == 'Floors': b_cat = BIC.OST_Floors
elif category == 'Walls': b_cat = BIC.OST_Walls
elif category == 'Roofs': b_cat = BIC.OST_Roofs

e_types = used_and_unused_types(b_cat)
keys = forms.SelectFromList.show(
	sorted(e_types.keys()),
	multiselect=True,
	button_name='Select Types to describe')
if not keys:   script.exit()
elems = [e_types[k] for k in keys]
params_name = [p.Definition.Name for p in elems[0].Parameters if not p.IsReadOnly and p.StorageType == DB.StorageType.String]
par_name = forms.SelectFromList.show(params_name,
				     				multiselect=False,
									button_name="Select parameter to set")

mat_name = lambda m: doc.GetElement(material).Name if doc.GetElement(material) else '-'
with revit.Transaction('M4B - compound elements description'):
	for e_type in elems:
		msg = ''
		enum = 0
		layers = get_layers(e_type)
		widths = layers[0]
		materials = layers[1]
		for width, material in zip(widths, materials):
			width = DB.UnitUtils.ConvertFromInternalUnits(width, DB.UnitTypeId.Millimeters)
			width = round(width, 1)
			enum += 1
			msg += '\n{}. {} ({} mm)'.format(enum, mat_name(material), width)
		# print(msg)

		e_type.LookupParameter(par_name).Set(msg)