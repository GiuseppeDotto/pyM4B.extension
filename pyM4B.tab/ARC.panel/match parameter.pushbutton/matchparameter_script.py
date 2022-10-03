
__doc__ = "Copy the instance parameter value of a selected elements to others."

from pyrevit import revit, DB, script, forms


doc = revit.doc
BIC = DB.BuiltInCategory


def get_par_value(par):
	if par.StorageType == DB.StorageType.String:
		return	par.AsString()
	elif par.StorageType == DB.StorageType.Double:
		return	par.AsDouble()
	elif par.StorageType == DB.StorageType.Integer:
		return	par.AsInteger()
	elif par.StorageType == DB.StorageType.ElementId:
		return	par.AsElementId()


def mark_element_as_renumbered(target_view, room):
    """Override element VG to transparent and halftone.

    Intended to mark processed renumbered elements visually.
    """
    ogs = DB.OverrideGraphicSettings()
    ogs.SetHalftone(True)
    ogs.SetSurfaceTransparency(100)
    target_view.SetElementOverrides(room.Id, ogs)


def unmark_renamed_elements(target_view, marked_element_ids):
    """Rest element VG to default."""
    for marked_element_id in marked_element_ids:
        ogs = DB.OverrideGraphicSettings()
        target_view.SetElementOverrides(marked_element_id, ogs)


# import DB

with forms.WarningBar(title='Select source element'):
	source = revit.pick_element()

	all_params = set([p.Definition.Name for p in source.Parameters])
	all_params = sorted(list(all_params))
	par_name = forms.SelectFromList.show(all_params, button_name='Select Parameter to copy')
	if not par_name:	script.exit()

	par_value = get_par_value(source.LookupParameter(par_name))


with forms.WarningBar(title='Select elements to edit. Press ESC to stop.'):
	vw = doc.ActiveView
	edited_ids = []
	with revit.TransactionGroup('M4B - Copy instance parameter'):
		for elem in revit.get_picked_elements():
			par = elem.LookupParameter(par_name)
			forms.alert_ifnot(par, 'Parameter not found.')

			if par:
				with revit.Transaction('A'):
					par.Set(par_value)
					mark_element_as_renumbered(vw, elem)
					edited_ids.append(elem.Id)

		with revit.Transaction('B'):
			unmark_renamed_elements(vw, edited_ids)