# Author:	Giuseppe Dotto

__doc__ =	"Duplicate with or without detail the selected views"\
			"and their Dependent views. In this last case, it will be checked if a scopebox"\
			"has been asigned to the dependent views, so to apply the same to the new views."

from pyrevit import revit, DB, UI
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms, script

from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,
							Separator, Button, CheckBox)

def duplicableview(view):
    return view.CanViewBeDuplicated(DB.ViewDuplicateOption.Duplicate)

def try_renaming(new_vw, nm, prefix, add, replace):
	try:
		if add:
			new_vw.Name = prefix + nm[:-6]
		elif replace:
			new_vw.Name = prefix + nm[len(prefix):-6]
	except:
		if add:
			new_vw.Name = prefix + nm
		elif replace:
			new_vw.Name = prefix + nm[len(prefix):]

doc = revit.doc

collector = DB.FilteredElementCollector(doc)
BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter

dup = DB.ViewDuplicateOption.Duplicate
wDet = DB.ViewDuplicateOption.WithDetailing
aDep = DB.ViewDuplicateOption.AsDependent


views = forms.select_views(filterfunc=duplicableview, use_selection=True)
if views:

	#vw.GetDependentViewIds()
	contexts = ["Duplicate", "WithDetailing", "Duplicate As Dependent"]
	qry = forms.CommandSwitchWindow.show(contexts, message='Select Option')
	if not qry:	script.Close()


	# CREATE FORMS
	allParName = [p.Definition.Name for p in views[0].Parameters if p.StorageType == DB.StorageType.String]
	components = [CheckBox('checkboxVT', 'Remove View Template'),
			Separator(),
			Label('New prefix:'),
			TextBox('textbox1', Text="XX"),
			CheckBox('checkbox1', 'Add prefix to the name'),
			CheckBox('checkbox2', 'Replace prefix to the name'),
			Separator(),
			CheckBox('checkbox3', 'Edit parameter'),
			Label('Pick Parameter to edit:'),
			ComboBox('combobox1', allParName),
			Label("New value"),
			TextBox('textbox2', Text="Default Value"),
			Separator(),
			Button('Select')]
	form = FlexForm('Duplicate Views - Options', components)
	form.show()
	
	# collect parameter name to change
	try:	prefix = form.values["textbox1"]
	except:	script.exit()

	if qry == "Duplicate":
		with revit.Transaction('duplicate views'):
			for vw in views:
				new_vw_id = vw.Duplicate(dup)
				new_vw = doc.GetElement(new_vw_id)
				nm = new_vw.Parameter[BIP.VIEW_NAME].AsString()
				# TRY RENAME
				try_renaming(new_vw, nm, prefix, form.values["checkbox1"], form.values["checkbox2"])
				# REMOVE TEMPLATE
				if form.values["checkboxVT"]:
					new_vw.ViewTemplateId = DB.ElementId.InvalidElementId
				# REPLACE PARAMETER
				if form.values["checkbox3"]:
					new_vw.LookupParameter(form.values["combobox1"]).Set(form.values["textbox2"])
				
	elif qry == "WithDetailing":
		with revit.Transaction('duplicate views with detailing'):
			for vw in views:
				new_vw_id = vw.Duplicate(wDet)
				new_vw = doc.GetElement(new_vw_id)
				nm = new_vw.Parameter[BIP.VIEW_NAME].AsString()
				# TRY RENAME
				try_renaming(new_vw, nm, prefix, form.values["checkbox1"], form.values["checkbox2"])
				# REMOVE TEMPLATE
				if form.values["checkboxVT"]:
					new_vw.ViewTemplateId = DB.ElementId.InvalidElementId
				# REPLACE PARAMETER
				if form.values["checkbox3"]:
					new_vw.LookupParameter(form.values["combobox1"]).Set(form.values["textbox2"])
				
	elif qry == "Duplicate As Dependent":
		with revit.Transaction('duplicate views as dependent'):
			for vw in views:
				new_vw_id = vw.Duplicate(aDep)
				new_vw = doc.GetElement(new_vw_id)
				nm = new_vw.Parameter[BIP.VIEW_NAME].AsString()
				# TRY RENAME
				try_renaming(new_vw, nm, prefix, form.values["checkbox1"], form.values["checkbox2"])
				# REMOVE TEMPLATE
				if form.values["checkboxVT"]:
					new_vw.ViewTemplateId = DB.ElementId.InvalidElementId
				# REPLACE PARAMETER
				if form.values["checkbox3"]:
					new_vw.LookupParameter(form.values["combobox1"]).Set(form.values["textbox2"])

