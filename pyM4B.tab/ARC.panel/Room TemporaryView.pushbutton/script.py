
__title__ = "Room\nTemporaryView"
__doc__ = "Enable Temporary View Properties and then turn ON visibility for "\
			"Rooms, its sub-categories and Rooms Separators Lines."

from pyrevit import revit, DB


def toogle_temporary_view():
	doc = revit.HOST_APP.doc
	vw = revit.HOST_APP.active_view
	BIC = DB.BuiltInCategory

	rooms_cat = DB.Category.GetCategory(doc, BIC.OST_Rooms)
	subCat = rooms_cat.SubCategories
	roomsSep_cat = DB.Category.GetCategory(doc, BIC.OST_RoomSeparationLines)

	overr_graph_sett = DB.OverrideGraphicSettings()
	overr_graph_sett.SetHalftone(True)


	# CHECK IF TEMP MODE IS ON
	if vw.GetTemporaryViewPropertiesName():
		# CHECK IF THE ROOMS ARE HIDDEN
		if DB.FilteredElementCollector(doc, vw.Id).OfCategory(BIC.OST_Rooms).GetElementCount() == 0:
			with revit.Transaction('Activate rooms visibility'):
				# OVERRIDE GRAPHICS
				vw.SetCategoryHidden(rooms_cat.Id, False)
				for c in subCat:
					vw.SetCategoryHidden(c.Id, False)
				vw.SetCategoryOverrides(rooms_cat.Id, overr_graph_sett)

				# TURN ON ROOM SEPARATOR
				vw.SetCategoryHidden(roomsSep_cat.Id, False)
				vw.SetCategoryOverrides(roomsSep_cat.Id, overr_graph_sett)
		
		# RESTORE THE VIEW
		else:
			with revit.Transaction('Deactivate rooms visibility'):
				vw.DisableTemporaryViewMode(DB.TemporaryViewMode.TemporaryViewProperties)
	
	else:
		with revit.TransactionGroup('Activate rooms visibility'):
			with revit.Transaction('A'):
				# TEMPORARY VIEW
				vw.EnableTemporaryViewPropertiesMode(vw.Id)
			
			with revit.Transaction('B'):
				# OVERRIDE GRAPHICS
				vw.SetCategoryHidden(rooms_cat.Id, False)
				for c in subCat:
					vw.SetCategoryHidden(c.Id, False)
				vw.SetCategoryOverrides(rooms_cat.Id, overr_graph_sett)

				# TURN ON ROOM SEPARATOR
				vw.SetCategoryHidden(roomsSep_cat.Id, False)
				vw.SetCategoryOverrides(roomsSep_cat.Id, overr_graph_sett)

toogle_temporary_view()	

