
__doc__ = "Report of which Design Options are visible in the selected views."

from pyrevit import revit, DB, forms, script
output = script.output.get_output()
# import DB

doc = revit.doc

opt = ['All Views', 'Select Views']
x = forms.CommandSwitchWindow.show(opt)
if x == opt[0]:
    views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType()
    views = [v for v in views if not v.IsTemplate]
elif x == opt[1]:
    views = forms.select_views()
else:   script.exit()

do_param = lambda e: e.get_Parameter(DB.BuiltInParameter.DESIGN_OPTION_PARAM).AsString()\
                    if e.get_Parameter(DB.BuiltInParameter.DESIGN_OPTION_PARAM)\
                    else None
data = []
for vw in views:
    elems = DB.FilteredElementCollector(doc, vw.Id).WhereElementIsNotElementType()
    visible_do = list(set([do_param(e) for e in elems]))
    # forms.alert_ifnot(visible_do[0],
    #                   'Design Options not active in current document',
    #                   exitscript=True )
    visible_do = ', '.join(sorted(visible_do))
    data.append( [vw.Name, visible_do] )

output.print_table(data, columns=['VIEW NAME', 'VISIBLE DESIGN OPTIONS'])
