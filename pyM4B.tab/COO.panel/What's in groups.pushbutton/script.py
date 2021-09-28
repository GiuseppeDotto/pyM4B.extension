
__title__ = "What's in\nGroups"

__doc__ =	"List of all the elements contained in the selected Model Group(s)."


from pyrevit import revit, DB, UI, script
from pyrevit import PyRevitException, PyRevitIOError
output = script.get_output()

from pyrevit import forms

doc = revit.doc
vw = doc.ActiveView
BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter
MGroup_gategory = DB.Category.GetCategory(doc, BIC.OST_IOSModelGroups).Id


# CHECK IF GROUPS HAVE BEEN SELECTED
groups = [i for i in revit.get_selection() if i.Category.Id == MGroup_gategory]
if len(groups) == 0:
	with forms.WarningBar(title="[{}] Pick Model Groups to inspect. Press ESC to exit.".format(len(groups))) as wb:
		tr = DB.Transaction(doc, 'Select elements')
		tr.Start()
		for picked_element in revit.get_picked_elements_by_category(BIC.OST_IOSModelGroups):
			groups.append(picked_element)
			wb.message_tb.Text = "[{}] Pick Model Groups to inspect. Press ESC to exit.".format(len(groups))
			vw.HideElementsTemporary(picked_element.GetMemberIds())
		tr.RollBack()

# COLLECT ALL ITEMS IN THE GROUPS
filter_category = lambda c: c and c.CategoryType == DB.CategoryType.Model and '<' not in c.Name
get_name = lambda e: e.Parameter[BIP.ELEM_FAMILY_AND_TYPE_PARAM].AsValueString()

print('List of the selected groups and their contents:')
for gr in groups:
	print("\n----------")
	print('{} GROUP NAME: {}'.format(output.linkify(gr.Id), gr.Name))
	sub = []
	for i in gr.GetMemberIds():
		elem = doc.GetElement(i)
		if filter_category(elem.Category) and get_name(elem):
			sub.append([output.linkify(i),
						elem.Category.Name,
						get_name(elem)])
						
	for j in sorted(sub, key=lambda row: row[1]):
		print('\t\t{} [{}] - "{}"'.format(j[0], j[1], j[2]))
	

