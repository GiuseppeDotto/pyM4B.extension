# Author:	Giuseppe Dotto, Macro4BIM

__doc__ =	"Return all the used and unused Sub-Categories of a defined parent category."

from pyrevit import revit, DB, script
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms
output = script.get_output()

doc = revit.doc

def get_family_Id(lst):
	out = []
	for i in lst:
		try:	out.append(i.Family.Id)
		except:	pass
	return	set(out)

def get_subCategoryName(d, main):
	for c in d.Settings.Categories:
		if c.Name == main.Name:
			for s in c.SubCategories:
				yield	c.Name + ' - ' + s.Name

def get_subCategoryList(families):
	out = []
	for f in families:
		try:
			out.append([f.Name, set(get_subCategoryName(doc.EditFamily(f), cat))])
		except:
			pass
	return	out
			

# GET CATEGORY
cat = doc.Settings.Categories
cat = dict( [[c.Name, c] for c in cat] )
k = forms.SelectFromList.show(sorted(cat.keys()), button_name='Select Category')
if not k: script.exit()
cat = cat[k]

# COLLECT ALL SUB-CATEGORIES

families = DB.FilteredElementCollector(doc).OfCategoryId(cat.Id).WhereElementIsElementType()
families_ids = get_family_Id(families) # avoiding exceptions such as WallsTypes
families = [doc.GetElement(i) for i in families_ids]

families_subCategories = dict( get_subCategoryList(families) ) # avoiding exceptions such as system families

subCat_name = lambda c, cs: c.Name + ' - ' + cs.Name
doc_subCategories = set([subCat_name(cat, sub_cat) for sub_cat in cat.SubCategories])
print('"{}" PROJECT SUB-CATEGORIES EXISTING IN FAMILIES:\n\n '.format(cat.Name))
for nm in sorted(doc_subCategories):
	
	if any([nm in x for x in families_subCategories.values()]):
		print(":white_heavy_check_mark: " + nm)
	else:
		print(":cross_mark: " + nm)

print('\nCHECKED FAMILIES: {}\n\n '.format(len(families)))

data = [['', '']]
for k in sorted(families_subCategories.keys()):
	for i in families_subCategories[k]-doc_subCategories:
		data.append([k, i])
	
	if data[-1][0] != k:
		data.append([k, None])

print('---------------\n"{}" SUB-CATEGORIES EXISTING IN FAMILIES ONLY:\n '.format(cat.Name))
header = ['FAMILY NAME', 'SUB-CATEGORIES MISSING FROM THE PROJECT']
output.print_table(data, columns=header)