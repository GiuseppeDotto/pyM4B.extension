__doc__ = "Add or replace a given prefix string to the name of the selected elements."\
		"\nTip: you can select Types or View from the Project Browser window."


from pyrevit import script, revit, DB, forms
from rpw.ui.forms import FlexForm, Label, ComboBox, TextBox, Separator, Button

# Global variables
doc = revit.doc


# CREATE INPUT FORM
components = [
			Label('Prefix'),
			TextBox('prefix', 'XX_'),
			ComboBox('to_add', {'to Add':True, 'to Replace': False}),
			Separator(),
			Button('Rename')]

form = FlexForm('Custom Prefix', components)
form.show()

new_prefix = form.vales.get('prefix')
to_add = form.vales.get('to_add')
if not new_prefix: script.exit()

# Rename elements
selection = revit.get_selection()
amount = 0
with revit.Transaction('M4B - Prefix'):
	for elem in selection:
		current_name = DB.Element.Name.__get__(elem)
		if to_add:
			new_name = new_prefix + current_name
		else:
			new_name = new_prefix + new_name[len(new_prefix):]
		if hasattr(elem, 'ViewType') or hasattr(elem, 'FamilyName'):
			elem.Name = new_name
		else:
			doc.GetElement(elem.GetTypeId()).Name = new_name
		amount += 1

forms.alert_ifnot(amount==0, '{} elements renamed.'.format(amount), warn_icon=False)
