
__doc__ = 'Select element of the same Type in selected views.\n\n'\
		'SHIFT-CLICK: select element of the same Class.'

from pyrevit import DB, revit, script, forms
from System.Collections.Generic import List
# import DB

doc = revit.doc
uidoc = revit.uidoc


with forms.WarningBar(title='Select source element'):
	source = revit.pick_element()
if not source: script.exit()

all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType()
vw_name = lambda v: '{}-{} ({})'.format(v.SheetNumber, v.Name, v.ViewType) if v.ViewType == DB.ViewType.DrawingSheet else '{} ({})'.format(v.Name, v.ViewType)
all_views = dict( [[vw_name(v), v] for v in sorted(all_views, key=vw_name)] )

# views = forms.select_views()
views = forms.SelectFromList.show(sorted(all_views.keys()), multiselect=True)
if not views: script.exit()
else:	views = [all_views[k] for k in views]
all_elems = []
for vw in views:
	temp = DB.FilteredElementCollector(doc, vw.Id).OfCategoryId(source.Category.Id).WhereElementIsNotElementType()
	if not __shiftclick__:
		all_elems.extend([e.Id for e in all_elems if e.GetTypeId() == source.GetTypeId()])

uidoc.Selection.SetElementIds(List[DB.ElementId](all_elems))
