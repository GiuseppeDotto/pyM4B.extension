
# copyright 2023, Macro4BIM (www.macro4bim.com)
# Author: Giuseppe Dotto

from pyrevit import script, forms, revit, DB
from rpw.ui.forms import FlexForm, Label, ComboBox, Separator, Button
# import DB

doc = revit.doc
vw = doc.ActiveView

tag_distribution = lambda l: [sum(l[:n])+l[n]/2.0 for n in range(len(l))]
def get_layers(legend_component):
	"""
	INPUT: legend_component\n
	OUTPUT: [all_widths, material_ids]
	"""
	w_type = legend_component.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).AsElementId()
	w_type = doc.GetElement(w_type)
	
	all_width = []
	materials_id = []
	if w_type.GetCompoundStructure():
		for l in reversed(w_type.GetCompoundStructure().GetLayers()):
			if l.Width: 
				all_width.append( l.Width )
				materials_id.append( l.MaterialId )
	return all_width, materials_id

def create_dimension_horizontal(legend_component, widths, horizontal=True):
 	if not widths: return None
  if horizontal:
    bb = legend_component.get_BoundingBox(vw)
    base = bb.Min
    tot_len = bb.Max.X - bb.Min.X
    vec = DB.XYZ(0,1,0)
    ln_base = DB.Line.CreateBound(base, base.Add(DB.XYZ(0.1,0,0)))
  else:
    bb = legend_component.get_BoundingBox(vw)
    base = bb.Min
    tot_len = bb.Max.Y - bb.Min.Y
    vec = DB.XYZ(1,0,0)
    ln_base = DB.Line.CreateBound(base, base.Add(DB.XYZ(0,0.1,0)))
  dt_crv = doc.Create.NewDetailCurve(vw, ln_base)
  ref_array_total = DB.ReferenceArray()

  ref_array_total.Append(DB.Reference(dt_crv))
  ref_array = DB.ReferenceArray()
  ref_array.Append(DB.Reference(dt_crv))
  progression = 0
	for w in widths:
		progression += w
		new_crv = DB.ElementTransformUtils.CopyElement(doc, dt_crv.Id, vec.Multiply(progression))
		ref_array.Append( DB.Reference(doc.GetElement(new_crv[0])) )
	ref_array_total.Append( DB.Reference(doc.GetElement(new_crv[0])) )

	dim_ln = DB.Line.CreateUnbound(base.Add(vec.CrossProduct(DB.XYZ(0,0,-1)).Multiply(tot_len+0.25)), vec)
	doc.Create.NewDimension(vw, dim_ln, ref_array)
	
	dim_ln = DB.Line.CreateUnbound(base.Add(vec.CrossProduct(DB.XYZ(0,0,-1)).Multiply(tot_len+0.5)), vec)
	doc.Create.NewDimension(vw, dim_ln, ref_array_total)

# SET USER INPUT
phases = DB.FilteredElementCollector(doc).OfClass(DB.Phase)
phases = dict( [[p.Name, p.Id] for p in phases] )
components = [Label('LEGEND COMPONENT ORIENTATION'),
			  ComboBox('orientation', ['Veritcal', 'Horizontal']),
			  Label('REFERENCE PROJECT PHASE. (where elements are created)'),
			  ComboBox('phase', phases.keys()),
			  Separator(),
			  Button('OK')]
form = FlexForm('Auto-Legend Components', components)
form.show()
if not form.values.get('orientation'):  script.exit()


with forms.WarningBar(title='SELECT A LEGEND COMPONENT'):
	legend = revit.pick_element()
	forms.alert_ifnot(legend.Category.BuiltInCategory == DB.BuiltInCategory.OST_LegendComponents,
					  'Select a Legend Component not selected.', exitscript=True)
with forms.WarningBar(title='SELECT THE MATERIAL TAG TO USE'):
	m_tag = revit.pick_element_by_category(DB.BuiltInCategory.OST_MaterialTags)
with forms.WarningBar(title='SELECT TEXT-NOTES TO READ AND COPY'):
	id_text = revit.pick_element_by_category(DB.BuiltInCategory.OST_TextNotes)
	par_name = id_text.Text[:-1]
	print('-'+par_name+'-')
	# script.exit()


# COLLECT TYPES TO ADD
phase_filetr = DB.ElementPhaseStatusFilter(phases[form.values['phase']],DB.ElementOnPhaseStatus.New)
cat_id = doc.GetElement(legend.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).AsElementId()).Category.Id
elems = DB.FilteredElementCollector(doc).OfCategoryId(cat_id).WhereElementIsNotElementType().WherePasses(phase_filetr)
elems = set([e.GetTypeId() for e in elems])
elems = set( [e for e in elems if 'curtain' not in doc.GetElement(e).FamilyName.lower()] )
# DEFINE FIXED TRANSLATION
translation = legend.get_BoundingBox(vw)
pt_base = translation.Min
translation = (translation.Max.X - translation.Min.X)*2

amount = len(elems)
with revit.TransactionGroup('Automatic Legend'):
	for x, e_type in enumerate(elems):
		with revit.Transaction('Copy and change Type'):
			new_elem = DB.ElementTransformUtils.CopyElement(doc, legend.Id, DB.XYZ(translation*(x+1),0,0))
			new_elem = doc.GetElement(new_elem[0])
			new_elem.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(e_type)
			print(new_elem)

		with revit.Transaction('place tags'): 
			ref = DB.Reference(new_elem)
			bb = new_elem.get_BoundingBox(vw)

			pts = []
			layers_info = get_layers(new_elem)
			spacing = 0.25
			pt = bb.Min
			for n, y in enumerate(tag_distribution(layers_info[0])):
				if form.values['orientation'] == "Horizontal":
					new_pt = pt.Add( DB.XYZ((n+1)*spacing, y, bb.Min.Z) )
					pts.append(new_pt)
				else:
					new_pt = pt.Add( DB.XYZ(y, (n+1)*spacing, bb.Min.Z) )
					pts.append(new_pt)
			if form.values['orientation'] == "Horizontal":
				Xs = [p.X for p in pts]
				for i, x in enumerate(Xs[::-1]):
					pts[i] = pts[i] = DB.XYZ(x, pts[i].Y, pts[i].Z)
			for n, pt in enumerate(pts):
				new_tag = DB.IndependentTag.Create(doc, m_tag.GetTypeId(), vw.Id, ref,
										True, DB.TagOrientation.Horizontal, pt)
				
				new_tag.LeaderEndCondition = DB.LeaderEndCondition.Free
				new_tag.SetLeaderEnd(ref,pt)
				if form.values['orientation'] == "Horizontal":
					new_tag.SetLeaderElbow(ref, DB.XYZ(pt.X, bb.Max.Y + (n+1)*spacing, pt.Z))
					new_tag.TagHeadPosition = DB.XYZ(bb.Max.X, bb.Max.Y +(n+1)*spacing, pt.Z)
				else:
					new_tag.SetLeaderElbow(ref, DB.XYZ(bb.Max.X, pt.Y, pt.Z))
					new_tag.TagHeadPosition = DB.XYZ(bb.Max.X+spacing, pt.Y, pt.Z)

		with revit.Transaction('Create Dimensions'):
			if form.values['orientation'] == "Horizontal":
				create_dimension_horizontal(new_elem, layers_info[0], horizontal=True)
			else:
				create_dimension_horizontal(new_elem, layers_info[0], horizontal=False)

		with revit.Transaction('CopyPaste and create text'):
			vec = bb.Min.Subtract(pt_base)
			new_txt = DB.ElementTransformUtils.CopyElement(doc, id_text.Id, vec)
			new_txt = doc.GetElement(new_txt[0])
			new_txt.Text = str(doc.GetElement(e_type).LookupParameter(par_name).AsValueString())
