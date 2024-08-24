from pyrevit import script, revit, DB, forms
try: import DB
except: pass
from rpw.ui.forms import FlexForm, Label, TextBox, Separator, Button

doc = revit.doc

# CREATE INPUT FORM
components = [Label('Search for:'),
			  TextBox('old', Text="search"),
			  Label('Replace with:'),
			  TextBox('new', Text="replace"),
			  Separator(),
			  Button('OK')]

form = FlexForm('Find and Replace', components)
form.show()

old_text = form.values.get('old')
new_text = form.values.get('new')
if not old_text: script.exit()

selection = revit.get_selection()
amount = 0
with revit.Transaction('M4B - FInd & Replace'):
	for elem in selection:
		current_name = DB.Element.Name.__get__(elem)
		if old_text in current_name:
			new_name = current_name.replace(old_text, new_text)
			if hasattr(elem, 'ViewType') or hasattr(elem, 'FamilyName'):
				elem.Name = new_name
			else:
				doc.GetElement(elem.GetTypeId()).Name = new_name
			amount += 1

forms.alert_ifnot(amount==0, '{} elements renamed.'.format(amount), warn_icon=False)