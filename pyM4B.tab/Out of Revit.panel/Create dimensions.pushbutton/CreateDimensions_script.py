# Author:	Giuseppe Dotto


__doc__ =	"Create a dimension picking all the Walls, Curtain Wall Panels and Mullions faces intersecting the given detail line.\n"\
			"In order for the tool find the reference faces, a 3D View containing the interested elements must be provided.\n"\
			"The function works only on walls, Curtain Wall Panels, Curtain Wall Mullions ans Revit Links."\
			"\n\nSHIFT-CLICK: Also element non perpendicular to the Line will be dimensioned by creating a new Detail Line "\
			"in the current view and letting the dimension reference to that."


from pyrevit import revit, DB, script
from pyrevit import PyRevitException, PyRevitIOError

from pyrevit import forms

from System.Collections.Generic import List
from math import pi
# import DB

doc = revit.doc
BIC = DB.BuiltInCategory


# PICK THE LINE AND COLLECT INTERSECTING WALL (and filter)
with forms.ProgressBar(title="Pick detail line") as pb:
	pb.update_progress(100)
	detail_line = revit.pick_element_by_category(BIC.OST_Lines)

if not detail_line:	script.exit()

# FIND 3D VIEW
all_3dviews = DB.FilteredElementCollector(doc).OfClass(DB.View3D)
all_3dviews = [v for v in all_3dviews if not v.IsTemplate]
all_3dviews.sort(key=lambda v:v.Name)

view3D = forms.SelectFromList.show(all_3dviews, multiselect=False, name_attr='Name', button_name='Select 3D View showing interested Walls and CurtainWalls')
if not view3D:	script.exit()


# COLLECT REFERENCE
dir_line = detail_line.GeometryCurve.Direction

rotation = DB.Transform.CreateRotation(DB.XYZ.BasisZ, pi/2)
dir_line_perp = detail_line.GeometryCurve.CreateTransformed(rotation).Direction

category_filter = DB.ElementMulticategoryFilter(List[DB.BuiltInCategory]\
					([BIC.OST_Walls, BIC.OST_CurtainWallPanels, BIC.OST_CurtainWallMullions, BIC.OST_RvtLinks,
       				BIC.OST_Floors, BIC.OST_Ceilings, BIC.OST_Roofs]))
ref_intersector = DB.ReferenceIntersector(category_filter, DB.FindReferenceTarget.Face, view3D)
ref_intersector.FindReferencesInRevitLinks = True

references = ref_intersector.Find(detail_line.GeometryCurve.Origin.Add(DB.XYZ(0,0,2500/304.8)), dir_line)
references = sorted(references, key=lambda r:r.Proximity)
references = [ref_with_context.GetReference() for ref_with_context in references]

forms.alert_ifnot(references, 'No References found.', exitscript=True)


get_face = lambda r: doc.GetElement(r).GetGeometryObjectFromReference(r)
get_normal = lambda r: get_face(r).ComputeNormal( get_face(r).Project(r.GlobalPoint).UVPoint ) \
						if get_face(r).Project(r.GlobalPoint) else get_face(r).ComputeNormal( DB.UV(0.5, 0.5) )
ref_normals = [get_normal(r) if get_face(r) else DB.XYZ(0,0,1) for r in references]


only_mullions = DB.ElementCategoryFilter(BIC.OST_CurtainWallMullions)
ref_intersector_mullions = DB.ReferenceIntersector(only_mullions, DB.FindReferenceTarget.Face, view3D)
viewed_mullions = True

# CREATE DIMENSION
with revit.Transaction('Create Dimension on Detail Line'):
	vw = doc.ActiveView
	ln = detail_line.GeometryCurve


	all_elem_in_view = DB.FilteredElementCollector(doc, vw.Id).WherePasses(category_filter).ToElementIds()


	ref_array = DB.ReferenceArray()
	ref_array_nr = 0
	pt = DB.XYZ(0,0,0)
	for r, ref_norm in zip(references, ref_normals):
		if r.ElementId in all_elem_in_view:

			# CHECK IF IS CURTAIN PANEL AND CHANGE ORIENTATION
			if doc.GetElement(r.ElementId).Category.Id == DB.Category.GetCategory(doc, BIC.OST_CurtainWallPanels).Id:
				ref_norm = DB.XYZ(ref_norm.Y, ref_norm.X, ref_norm.Z)

				# GET THE CLOSEST MULLION
				below_mullion = ref_intersector_mullions.FindNearest(r.GlobalPoint, DB.XYZ(0,0,-1))
				if below_mullion:
					below_mullion = below_mullion.GetReference()

					if viewed_mullions:
						r = ref_intersector_mullions.FindNearest(below_mullion.GlobalPoint.Add(DB.XYZ(0,0,-0.1)), dir_line.Multiply(-1))
						r = r.GetReference()
						viewed_mullions = not viewed_mullions
					else:
						r = ref_intersector_mullions.FindNearest(below_mullion.GlobalPoint.Add(DB.XYZ(0,0,-0.1)), dir_line)
						r = r.GetReference()
						viewed_mullions = not viewed_mullions
				else:
					viewed_mullions = not viewed_mullions


			# CHECK IF IS PERPENDICULAR
			if abs(dir_line.DotProduct(ref_norm)) == 1:
				if pt.DistanceTo(r.GlobalPoint) > 0.01:
					ref_array.Append(r)
					ref_array_nr += 1
					pt = r.GlobalPoint
			elif __shiftclick__:
				if pt.DistanceTo(r.GlobalPoint) > 0.01:
					pt = r.GlobalPoint
					temp_ln = DB.Line.CreateBound(pt, pt.Add(dir_line_perp.Multiply(0.1)))
					new_crv = doc.Create.NewDetailCurve(vw, temp_ln)
					ref_array.Append(new_crv.GeometryCurve.Reference)
					ref_array_nr += 1


	if ref_array_nr!=0:
			doc.Create.NewDimension(vw, ln, ref_array)
	else:
		forms.alert('0 references found.')

