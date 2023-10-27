# Author:	Giuseppe Dotto

__doc__ =	"Delete multiple viewTemplates at a time, selecting them through their name."

from pyrevit import revit, DB, script
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms


doc = revit.doc


allViewClass = DB.FilteredElementCollector(doc).OfClass(DB.View)
allViewClass = sorted(allViewClass, key=lambda v: v.Name)

all_vTemplates = set([v.Id for v in allViewClass if v.IsTemplate])
used_vTemplate = set([v.ViewTemplateId for v in allViewClass if not v.IsTemplate and v.ViewTemplateId])
unused_vTemplate = all_vTemplates-used_vTemplate

# SORTING
sort_by_name = lambda lst: zip(* sorted([(doc.GetElement(i).Name, doc.GetElement(i)) for i in lst if doc.GetElement(i)]) )[1]

view_templates = {'Used': sort_by_name(used_vTemplate), 
				'Unused': sort_by_name(unused_vTemplate)}


# MAKE FORMS		
toDel = forms.SelectFromList.show(view_templates, title = "select ViewTemplates to delete",
							name_attr='Name', multiselect=True, button_name='Delete ViewTemplates')

# if not toDel:	script.exit()

# elif forms.alert("delete {} ViewTemplates?".format(len(toDel)), yes = True, no = True):
if toDel and forms.alert("delete {} ViewTemplates?".format(len(toDel)), yes = True, no = True):
	with revit.Transaction('Delete Templates'):
		for k in toDel:
			doc.Delete(k.Id)

