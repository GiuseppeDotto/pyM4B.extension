
__doc__ = 'Move the selected VIewport to the front.'\
		'The tool actually delete and place back the view on the sheet.'


from pyrevit import script, revit, DB, forms


BIC = DB.BuiltInCategory

doc = revit.doc
uidoc = revit.uidoc


with forms.WarningBar(title='Pick Viewports to edit - ESC to stop'):
	with revit.TransactionGroup('Viewports to Front'):
		for vport in revit.get_picked_elements_by_category(BIC.OST_Viewports):
			with revit.Transaction('Move Viewport'):
				# GET CENTRAL POINT & VIEW/ DELETE VPORT / PLACE BACK
				pt = vport.GetBoxCenter()
				viewsheet_id = vport.OwnerViewId
				view_id = vport.ViewId
				viewportType_id = vport.GetTypeId()

				doc.Delete(vport.Id)

				new_vp = DB.Viewport.Create(doc, viewsheet_id, view_id, pt)
				new_vp.ChangeTypeId(viewportType_id)

			uidoc.RefreshActiveView()