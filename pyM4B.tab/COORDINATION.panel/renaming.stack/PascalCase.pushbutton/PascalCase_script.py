__doc__ = "Edit the Family or the Type names of the selected elements rewriting "\
		"in Pascal-Case (ExampleTextOfPascalCase). The words can be recognized "\
		"only if there is a space between them in the current name."\
		"\nTip: you can also select Types from the Project Browser window."


from pyrevit import script, revit, DB
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox,\
						Separator, Button, TaskDialog, Alert)


def ask_confirmation(lst, obj):
	dialog = TaskDialog('Rename {} {}?'.format(len(lst), obj), buttons=['Yes', 'No'])
	if dialog.show() == 'No':
		script.exit()

def to_PascalCase(current):
	new = ''
	for sub in current.split(' '):
		if len(sub) > 0:
			new += sub[0].upper() + sub[1:].lower()
	return	new


selection = revit.get_selection()
if len(selection) == 0:
	Alert('Select at least one element or type.',
		header='No elements have been selected.',
		exit=True)

# CREATE INPUT FORM
components = [Label('Select elements of the same'),
			ComboBox('combobox1', ['Family Name', 'FamilyType Name']),
			Separator(),
			Button('OK')]

form = FlexForm('Choose what to rename', components)
form.show()

# SCRIPT
BIP = DB.BuiltInParameter
typ_name = lambda x: x.Parameter[BIP.SYMBOL_NAME_PARAM].AsString()
accepted_classes = [DB.FamilySymbol, DB.WallType, DB.FloorType, DB.CeilingType, DB.RoofType]

if form.values['combobox1'] == 'Family Name':
	selected_fam = []
	for e in selection:
		if e.GetType() == DB.FamilySymbol:
			selected_fam.append(e.Family.Id)
		else:
			selected_fam.append(e.Symbol.Family.Id)
	selected_fam = set(selected_fam)

	ask_confirmation(selected_fam, 'Families')
	with revit.Transaction('Rename Families'):	
		for f in selected_fam:
			f = revit.doc.GetElement(f)
			f.Name = to_PascalCase(f.Name)

elif form.values['combobox1'] == 'FamilyType Name':
	selected_type = []
	for e in selection:
		#if e.GetType() == DB.FamilySymbol:
		if any([e.GetType() == x for x in accepted_classes]):
			selected_type.append(e.Id)
		else:
			selected_type.append(e.Symbol.Id)
	selected_type = set(selected_type)
	
	ask_confirmation(selected_type, 'Types')
	with revit.Transaction('Rename Types'):
		for t in selected_type:
			t = revit.doc.GetElement(t)
			t.Name = to_PascalCase(typ_name(t))


