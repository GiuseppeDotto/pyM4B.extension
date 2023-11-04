
from pyrevit import revit, DB

doc = revit.doc

compound_categories = [DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Walls).Id,
                       DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Floors).Id,
                       DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Roofs).Id,
                       DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Ceilings).Id]
def get_info(legend):
    """
    Inform weather the given legend compoenent represent a compound object 
    and if its design is horizontal or vertical.

    Args:
        legend (DB.Element): The legend component to inspect
    Return:
        [is_compound (bool), is_horizontal (bool)]
    """
    cat_id = doc.GetElement(legend.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).AsElementId()).Category.Id
    if cat_id in compound_categories and cat_id == compound_categories[0]:
        return [True, legend.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT_VIEW).AsInteger() == -8]
    elif cat_id in compound_categories:
        return [True, True]
    else:
        return [False, False]

_tag_distribution = lambda l: [sum(l[:n])+l[n]/2.0 for n in range(len(l))]
def _get_layers(legend_component):
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

def create_material_tags(new_elem, m_tag, vw, is_horizontal=True):
    """
    Place one material tag per layer on the given compound object.

    Args:
        new_elem (DB.Element): The Legend compoenent
        m_tag (DB.ElementId): The Id of the material tag FamilySymbol the is intended to use
        vw (DB.View): the Legend view where the element sits
        is_horizontal (bool): Orientation of the provided legend component
    Return:
        The collection of the created material tags
    """
    ref = DB.Reference(new_elem)
    bb = new_elem.get_BoundingBox(vw)

    pts = []
    spacing = 0.25
    pt = bb.Min
    for n, y in enumerate(_tag_distribution(_get_layers(new_elem)[0])):
        if is_horizontal:
            new_pt = pt.Add( DB.XYZ((n+1)*spacing, y, bb.Min.Z) )
            pts.append(new_pt)
        else:
            new_pt = pt.Add( DB.XYZ(y, (n+1)*spacing, bb.Min.Z) )
            pts.append(new_pt)
    if is_horizontal:
        Xs = [p.X for p in pts]
        for i, x in enumerate(Xs[::-1]):
            pts[i] = DB.XYZ(x, pts[i].Y, pts[i].Z)
    for n, pt in enumerate(pts):
        new_tag = DB.IndependentTag.Create(doc, m_tag, vw.Id, ref,
                                True, DB.TagOrientation.Horizontal, pt)
        
        new_tag.LeaderEndCondition = DB.LeaderEndCondition.Free
        new_tag.SetLeaderEnd(ref,pt)
        if is_horizontal:
            new_tag.SetLeaderElbow(ref, DB.XYZ(pt.X, bb.Max.Y + (n+1)*spacing, pt.Z))
            new_tag.TagHeadPosition = DB.XYZ(bb.Max.X, bb.Max.Y +(n+1)*spacing, pt.Z)
        else:
            new_tag.SetLeaderElbow(ref, DB.XYZ(bb.Max.X, pt.Y, pt.Z))
            new_tag.TagHeadPosition = DB.XYZ(bb.Max.X+spacing, pt.Y, pt.Z)


def create_dimension_horizontal(legend_component, vw, horizontal=True):
    if not _get_layers(legend_component)[0]:
        return	None
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
    for w in _get_layers(legend_component)[0]:
        progression += w
        new_crv = DB.ElementTransformUtils.CopyElement(doc, dt_crv.Id, vec.Multiply(progression))
        ref_array.Append( DB.Reference(doc.GetElement(new_crv[0])) )
    ref_array_total.Append( DB.Reference(doc.GetElement(new_crv[0])) )

    if horizontal:	trasl = 0
    else:	trasl = tot_len
    dim_ln = DB.Line.CreateUnbound(base.Add(vec.CrossProduct(DB.XYZ(0,0,-1)).Multiply(trasl+0.25)), vec)
    doc.Create.NewDimension(vw, dim_ln, ref_array)
    
    dim_ln = DB.Line.CreateUnbound(base.Add(vec.CrossProduct(DB.XYZ(0,0,-1)).Multiply(trasl+0.5)), vec)
    doc.Create.NewDimension(vw, dim_ln, ref_array_total)

def _get_value(par):
    if par and par.StorageType == DB.StorageType.String:
        if par.AsString():
            return par.AsString()
        else:	return ''
    elif par:
        if par.AsValueString():
            return par.AsValueString()
        else:	return ''
    else:
        return '---'

def set_TextNote(textNote, type_id):
    """
    Update a give TextNote containing parameters' name in { }

    Args:
        textNote (DB.TextNote): the TextNote to edit.
        type_id (DB.ElementId): The id of the element type from which to extract the parameters
    """
    p_names = []
    for x in textNote.Text.split('{'):
        if '}' in x:	p_names.append(x[:x.index('}')])
    for p in p_names:
        textNote.Text = textNote.Text.replace('{'+p+'}', 
                                              _get_value(doc.GetElement(type_id).LookupParameter(p)))
    # textNote.Text = textNote.Text.replace('{', '').replace('}', '')