__doc__ = "Add or replace a given prefix string to the name of the selected elements."\
		"\nTip: you can select Types or View from the Project Browser window."


from pyrevit import script, revit, DB
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox,\
						Separator, Button, TaskDialog, Alert)

import RenamingTools

def ask_confirmation(lst, obj, all_names):
	exp = ''
	for i in all_names:	exp += "{}\n".format(i)
	dialog = TaskDialog('Rename {} {}?'.format(len(lst), obj), buttons=['Yes', 'No'],
						expanded_content=exp)
	if dialog.show() == 'No':
		script.exit()


selection = revit.get_selection()
if len(selection) == 0:
	Alert('Select at least one element or type.',
		header='No elements have been selected.',
		exit=True)

# CREATE INPUT FORM
components = [Label('Select elements of the same'),
			ComboBox('combobox1', ['Family and/or View Name', 'FamilyType']),
			Label('Prefix'),
			TextBox('textbox1', 'XX_'),
			ComboBox('combobox2', ['to Add', 'to Replace']),
			Separator(),
			Button('Rename')]

form = FlexForm('Choose what to rename', components)
form.show()

# COLLECT INPUT
try:
	toRename = form.values['combobox1']
	prefix = form.values['textbox1']
	toAdd = form.values['combobox2'] == 'to Add'
except:
	script.exit()


# SCRIPT
BIP = DB.BuiltInParameter
typ_name = lambda x: x.Parameter[BIP.SYMBOL_NAME_PARAM].AsString()


if form.values['combobox1'] == 'Family and/or View Name':
	selected_fam = [RenamingTools.get_family(x) for x in selection]
	selected_fam = set(selected_fam)

	all_elems = [revit.doc.GetElement(f) for f in selected_fam]
	all_names = sorted([f.Name for f in all_elems])
	ask_confirmation(selected_fam, 'Families/Views', all_names)
	with revit.Transaction('Rename Families'):	
		for f in all_elems:
			f.Name = RenamingTools.add_prefix(f.Name, prefix, toAdd)

elif form.values['combobox1'] == 'FamilyType':
	selected_type = [RenamingTools.get_type(x) for x in selection]
	selected_type = set(selected_type)

	all_elems = [revit.doc.GetElement(t) for t in selected_type]	
	all_names = sorted([typ_name(t) for t in all_elems])
	ask_confirmation(selected_type, 'Types', all_names)
	with revit.Transaction('Rename Types'):
		for t in all_elems:
			t.Name = RenamingTools.add_prefix(typ_name(t), prefix, toAdd)


