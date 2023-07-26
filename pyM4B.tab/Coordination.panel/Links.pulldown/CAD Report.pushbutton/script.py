
__title__ = 'CAD\nReport'
__doc__ = 'Report on the CAD linked/imported in the active document and the Imported Categories'

from pyrevit import revit, DB
from pyrevit import output

output = output.get_output()
doc = revit.doc

all_links = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).WhereElementIsNotElementType()
#.OwnerViewId
header = ['NAME', 'LINK/IMPORT', 'VIEW SPECIFIC', "OWNER VIEW"]

def get_info(e):
	try:	
		out = [e.Category.Name]
		out.append(output.linkify(e.Id, title=out[0]))
	except:	
		out = ['zzz']
		out.append(output.linkify(e.Id))
	if e.IsLinked:	out.append('Link')
	else:	out.append('Import')
	out.append(e.ViewSpecific)
	owi = e.OwnerViewId
	if doc.GetElement(owi):	out.append(doc.GetElement(owi).Name)
	else:	out.append(owi)
	return	out

data = sorted([get_info(i) for i in all_links])
data = [s[1:] for s in data]

output.print_table(data, columns=header)

# REPORT TE IMPORTED INSTANCES
print('-----\nImported Categories pointing at imported instance:\n\n\n')
links_names = [i.Category.Name for i in all_links]
import_categories = sorted([c.Name for c in doc.Settings.Categories if '.dwg' in c.Name])
for c in import_categories:
	if any([x in c for x in links_names]):
		print(":white_heavy_check_mark: " + c)
	else:
		print(":cross_mark: " + c)

