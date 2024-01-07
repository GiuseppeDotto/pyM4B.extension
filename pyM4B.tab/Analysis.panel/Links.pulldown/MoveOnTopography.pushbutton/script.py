
from pyrevit import DB, revit, forms
# import DB

doc = revit.doc
vw = doc.ActiveView

def move_link_on_topography(link_instance, topography):
    with revit.Transaction('move link'):
        try:
            link_doc = link_instance.GetLinkDocument()
            base_pt = DB.FilteredElementCollector(link_doc).OfCategory(DB.BuiltInCategory.OST_ProjectBasePoint).FirstElement()
            transform = link_instance.GetTotalTransform()
            pt = transform.OfPoint(base_pt.Position)
        
        
            ref_int = DB.ReferenceIntersector(topography.Id, DB.FindReferenceTarget.All, vw)
            distance = ref_int.FindNearest(pt, DB.XYZ(0,0,-1)).Proximity
        
            DB.ElementTransformUtils.MoveElement(doc, link_instance.Id, DB.XYZ(0,0,-1*distance))
            return [link_instance.Name, True]
        except Exception as ex:
            return [link_instance.Name, str(ex)]


with forms.WarningBar(title='Select first the Revit Link to move, then the Topography. ESC to stop.'):
    with revit.TransactionGroup('MovingLinks'):
        for link_instance in revit.get_picked_elements_by_category(DB.BuiltInCategory.OST_RvtLinks):
            for topo in revit.get_picked_elements_by_category(DB.BuiltInCategory.OST_Topography):
                move_link_on_topography(link_instance, topo)
                break
