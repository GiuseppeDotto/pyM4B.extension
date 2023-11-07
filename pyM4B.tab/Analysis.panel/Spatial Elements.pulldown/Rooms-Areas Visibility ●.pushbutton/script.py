
from System.Collections.Generic import List
from pyrevit import revit, DB
# import DB
doc = revit.HOST_APP.doc
vw = revit.HOST_APP.active_view
BIC = DB.BuiltInCategory

def turn_categories_on():
	area_cat = DB.Category.GetCategory(doc, BIC.OST_Areas)
	rooms_cat = DB.Category.GetCategory(doc, BIC.OST_Rooms)
	subCat = list(rooms_cat.SubCategories)
	subCat += list(area_cat.SubCategories)
	categories = [area_cat, rooms_cat,
			   DB.Category.GetCategory(doc, BIC.OST_RoomSeparationLines),
			   DB.Category.GetCategory(doc, BIC.OST_AreaSchemeLines)]
	
	overr_graph_sett = DB.OverrideGraphicSettings()
	overr_graph_sett.SetHalftone(True)
	
	# TURN ON CATEGORIES AND OVERRIDE GRAPHICS
	for c in categories:
		vw.SetCategoryHidden(c.Id, False)
		vw.SetCategoryOverrides(c.Id, overr_graph_sett)
	for c in subCat:
		vw.SetCategoryHidden(c.Id, False)

	# ISOLATE CATEGORIES
	if __shiftclick__:
		categories = List[DB.ElementId]([c.Id for c in categories])
		vw.IsolateCategoriesTemporary(categories)


def toogle_temporary_view():
	with revit.TransactionGroup('Activate Spatial Element visibility'):
		with revit.Transaction('A'):
			# TEMPORARY VIEW
			vw.EnableTemporaryViewPropertiesMode(vw.Id)
		
		with revit.Transaction('B'):
			turn_categories_on()


toogle_temporary_view()

