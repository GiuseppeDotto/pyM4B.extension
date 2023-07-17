
# copyright 2023, Macro4BIM (www.macro4bim.com)
# Author: Giuseppe Dotto

from pyrevit import DB, forms, revit, script
# import DB

__title__ = 'Auto\nLegend'

doc = revit.doc
vw = doc.ActiveView

def get_layers(elem):
	w_type = elem.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).AsElementId()
	w_type = doc.GetElement(w_type)
	
	all_width = []
	all_positions = []
	progressive = 0
	if w_type.GetCompoundStructure():
		for l in reversed(w_type.GetCompoundStructure().GetLayers()):
			if l.Width: 
				progressive += l.Width
				all_positions.append(progressive - l.Width/2)
				all_width.append( l.Width )
	return all_positions, all_width


def get_basePt(elem):
	widths = get_layers(elem)[1]
	bb = elem.get_BoundingBox(vw)
	base = (bb.Min.X+bb.Max.X)/2 - sum(widths)/2
	return	DB.XYZ(base, bb.Min.Y, 0)

def material_tag(base, elem, tag_id):
	y = 0.2
	for n, x in enumerate(get_layers(elem)[0]):
		pt = base.Add(DB.XYZ(x,y*(n+1),0))
		new_tag = DB.IndependentTag.Create( doc, tag_id, vw.Id,
							DB.Reference(elem), True,
							DB.TagOrientation.Horizontal, pt)
		
		new_tag.SetLeaderEnd(DB.Reference(elem), pt)
		new_tag.TagHeadPosition = DB.XYZ(elem.get_BoundingBox(vw).Max.X + 0.5, pt.Y, 0)
		


def create_dimension(base, elem):
	ln_base = DB.Line.CreateBound(base, base.Add(DB.XYZ(0,0.1,0)))
	dt_crv = doc.Create.NewDetailCurve(vw, ln_base)
	
	widths = get_layers(elem)[1]
	progression = 0
	
	ref_array_total = DB.ReferenceArray()
	ref_array_total.Append(DB.Reference(dt_crv))
	ref_array = DB.ReferenceArray()
	ref_array.Append(DB.Reference(dt_crv))
	for w in widths:
		progression += w
		new_crv = DB.ElementTransformUtils.CopyElement(doc, dt_crv.Id, DB.XYZ(progression,0,0))
		ref_array.Append( DB.Reference(doc.GetElement(new_crv[0])) )
	ref_array_total.Append( DB.Reference(doc.GetElement(new_crv[0])) )

	dim_ln = DB.Line.CreateUnbound(base.Add(DB.XYZ(0,3.5,0)), DB.XYZ(1,0,0))
	doc.Create.NewDimension(vw, dim_ln, ref_array)
	
	dim_ln = DB.Line.CreateUnbound(base.Add(DB.XYZ(0,3.8,0)), DB.XYZ(1,0,0))
	doc.Create.NewDimension(vw, dim_ln, ref_array_total)



def create_title(base, elem, ref_text):
	# base = base.Add( XYZ(sum(get_layers(elem)[1])/2,0,0) ) # move to center
	w_type = elem.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).AsElementId()
	w_type = doc.GetElement(w_type)
	
	par = w_type.LookupParameter( ref_text.Text[:-1] )
	if par:
		value = par.AsString()
		if not value:   value = '-'
		DB.TextNote.Create(doc, vw.Id, base.Add(DB.XYZ(0,-0.2,0)), value, ref_text.GetTypeId())


# CHECK YOU ARE IN LEGEND VIEW
forms.alert_ifnot(vw.ViewType == DB.ViewType.Legend, 'The function only works in Legend View.', exitscript=True )

# COLLECT INPUT
with forms.WarningBar(title='SELECT LEGEND COMPONENT'):
	source_component = revit.pick_element()
	if not source_component: script.exit()
	forms.alert_ifnot(source_component.Parameter[DB.BuiltInParameter.LEGEND_COMPONENT],
					"Select a Legend Component", exitscript=True)
with forms.WarningBar(title='SELECT MATERIAL TAG'):
	source_tag = revit.pick_element_by_category(DB.BuiltInCategory.OST_MaterialTags)
	if not source_tag: script.exit()
with forms.WarningBar(title='SELECT TEXT TYPE WITH PARAMETER NAME'):
	ref_text = revit.pick_element_by_category(DB.BuiltInCategory.OST_TextNotes)
	if not ref_text: script.exit()

all_wallType_ids = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
all_wallType_ids = set( [w.WallType.Id for w in all_wallType_ids] )
all_wallType_ids = [wt for wt in all_wallType_ids if doc.GetElement(wt).GetCompoundStructure()]


spacing = 3.5
with revit.Transaction('Automatic Walls Legend'):
	for n, wall_t in enumerate(all_wallType_ids):
		new_elem = DB.ElementTransformUtils.CopyElement(doc, source_component.Id, DB.XYZ(spacing + spacing*n,0,0))
		new_elem = doc.GetElement(new_elem[0])
		new_elem.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(wall_t)        
		
		base = get_basePt(new_elem)
		
		material_tag(base, new_elem, source_tag.GetTypeId())
		create_dimension(base, new_elem)
		create_title(base, new_elem, ref_text)
		

