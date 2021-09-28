
__title__ = "What's in\nGroups"

__doc__ =	"List of all the elements contained in the selected Model Group(s)."


from pyrevit import revit, DB, UI, script
from pyrevit import PyRevitException, PyRevitIOError
output = script.get_output()


from pyrevit import forms

doc = revit.doc
BIC = DB.BuiltInCategory
MGroup_gategory = DB.Category.GetCategory(doc, BIC.OST_IOSModelGroups).Id


# CHECK IF GROUPS HAVE BEEN SELECTED
groups = [i for i in revit.get_selection() if i.Category.Id == MGroup_gategory]
if len(groups) == 0:
	with forms.WarningBar(title='Pick Model Groups to inspect.'):
		groups = revit.pick_elements_by_category(BIC.OST_IOSModelGroups)

# COLLECT ALL ITEMS IN THE GROUPS
filter_category = lambda c: c and c.CategoryType == DB.CategoryType.Model and '<' not in c.Name

for gr in groups:
	print('{}; GROUP NAME: {}\n'.format(output.linkify(gr.Id), gr.Name))
	for i in gr.GetMemberIds():
		elem = doc.GetElement(i)
		sub = []
		if filter_category(elem.Category):
			sub.append([elem.Category.Name, DB.Element.Name.__get__(elem), i])
			# print('{}; Category: {}; Name: {}'.format(output.linkify(i),
			# 										elem.Category.Name,
			# 										DB.Element.Name.__get__(elem)))
		for j in sorted(sub):
			print('{}; CATEGORY: {}; NAME: {}'.format(output.linkify(j[2]), j[0], j[1]))
	print("----------\n\n")	


