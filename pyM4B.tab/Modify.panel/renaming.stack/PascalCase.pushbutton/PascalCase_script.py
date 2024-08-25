
from pyrevit import script, revit, DB, forms

def to_PascalCase(current):
	new = ''
	for sub in current.split(' '):
		if len(sub) > 0:
			new += sub[0].upper() + sub[1:].lower()
	return	new

# Global variables
doc = revit.doc

selection = revit.get_selection()
amount = 0
with revit.Transaction('M4B - to PascaleCase'):
	for elem in selection:
		current_name = DB.Element.Name.__get__(elem)
		to_PascalCase(current_name)
		if hasattr(elem, 'ViewType') or hasattr(elem, 'FamilyName'):
			elem.Name = to_PascalCase(current_name)
		else:
			doc.GetElement(elem.GetTypeId()).Name = to_PascalCase(current_name)
		amount += 1

forms.alert_ifnot(amount==0, '{} elements renamed.'.format(amount), warn_icon=False)
