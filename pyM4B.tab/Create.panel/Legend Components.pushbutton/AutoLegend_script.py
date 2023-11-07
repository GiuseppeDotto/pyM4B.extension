
# copyright 2023, Macro4BIM (www.macro4bim.com)
# Author: Giuseppe Dotto
import os, sys
sys.path.append( os.path.dirname(os.path.dirname(__file__)) )
from pyrevit import script, forms, revit, DB
from rpw.ui.forms import FlexForm, Label, ComboBox, Separator, Button
import m4b_legend
# import DB

doc = revit.doc
vw = doc.ActiveView


symbol_name = lambda sy: '{}: {}'.format(sy.FamilyName,
										sy.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString())

# Ask which is the project phase to study
phases = DB.FilteredElementCollector(doc).OfClass(DB.Phase)
phases = dict( [[p.Name, p.Id] for p in phases] )
phase = forms.CommandSwitchWindow.show(phases, message='Select Phase')
if not phase:  script.exit()
else:	phase = phases[phase]

# Select all the source elements: Legend component, TextNote
with forms.WarningBar(title='SELECT A LEGEND COMPONENT'):
	legend = revit.pick_element()
	forms.alert_ifnot(legend.Category.BuiltInCategory == DB.BuiltInCategory.OST_LegendComponents,
					  'Select a Legend Component.', exitscript=True)
# Define legend component's characteritics
is_compound, is_horizontal = m4b_legend.get_info(legend)

with forms.WarningBar(title='SELECT TEXT-NOTES TO READ AND COPY - Press "Esc" to skip'):
	id_text = revit.pick_element_by_category(DB.BuiltInCategory.OST_TextNotes)

# Select Material Tags Type if is compound object
if is_compound:
	m_tags = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_MaterialTags).WhereElementIsElementType()
	m_tags = dict([[symbol_name(t), t] for t in m_tags])
	m_tag = forms.SelectFromList.show(['None']+sorted(m_tags.keys()),
									multiselect=False,
									button_name='Select Material Tag Type')
	if m_tag and m_tag != 'None':
		m_tag = m_tags[m_tag].Id

# COLLECT TYPES TO ADD
phase_filetr = DB.ElementPhaseStatusFilter(phase,DB.ElementOnPhaseStatus.New)
cat_id = doc.GetElement(legend.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).AsElementId()).Category.Id
elems = DB.FilteredElementCollector(doc).OfCategoryId(cat_id).WhereElementIsNotElementType().WherePasses(phase_filetr)
elems = set([e.GetTypeId() for e in elems])
# Skip Curtain Walls
if cat_id == DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Walls).Id:
	elems = [w_type for w_type in elems if doc.GetElement(w_type).Kind == DB.WallKind.Basic]


# DEFINE FIXED TRANSLATION
translation = legend.get_BoundingBox(vw)
pt_base = translation.Min
translation = (translation.Max.X - translation.Min.X)*2
if not is_horizontal:	translation *= 2

amount = len(elems)
with revit.TransactionGroup('Automatic Legend'):
	for x, e_type in enumerate(elems):
		with revit.Transaction('Copy and change Type'):
			new_elem = DB.ElementTransformUtils.CopyElement(doc, legend.Id, DB.XYZ(translation*(x+1),0,0))
			new_elem = doc.GetElement(new_elem[0])
			new_elem.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(e_type)
			print(new_elem)

		if id_text:
			with revit.Transaction('CopyPaste and create text'):
				vec = new_elem.get_BoundingBox(vw).Min.Subtract(pt_base)
				new_txt = DB.ElementTransformUtils.CopyElement(doc, id_text.Id, vec)
				new_txt = doc.GetElement(new_txt[0])
				m4b_legend.set_TextNote(new_txt, e_type)
		if is_compound:
			if m_tag and m_tag != 'None':
				with revit.Transaction('place tags'):
					m4b_legend.create_material_tags(new_elem, m_tag, vw, is_horizontal)

			with revit.Transaction('Create Dimensions'):
				m4b_legend.create_dimension_horizontal(new_elem, vw, is_horizontal)

script.get_output().close()
with revit.Transaction('Automatic Legend - Delete source elements'):
	doc.Delete(legend.Id)
	if id_text:	doc.Delete(id_text.Id)