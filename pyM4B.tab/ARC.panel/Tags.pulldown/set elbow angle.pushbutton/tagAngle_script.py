
__doc__ = 'Set Elbow angle for the selected tags.'


import math
from pyrevit import DB, revit, forms, script
from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, CheckBox,\
						Separator, Button, TaskDialog, Alert)
# import DB


doc = revit.doc

# USER INPUT
components = [CheckBox('all_in_view', 'Select all in active view: '),
			Separator(),
			Label('New angle [degrees]:'),
			TextBox('angle', Text="45"),
			Separator(),
			Button('OK')]

form = FlexForm('Change Tags angle', components)
form.show()

if not form.values:    script.exit()

angle = form.values['angle']
forms.alert_ifnot(angle.isnumeric(), 'Please specify numeric values for "angle"',
					exitscript=True)
					
angle = float(angle)
	

if form.values['all_in_view']:
	BIC = DB.BuiltInCategory
	vw = doc.ActiveView
	sel_tags = DB.FilteredElementCollector(doc, vw.Id).OfClass(DB.IndependentTag)

else:
	with forms.WarningBar(title='Select tags'):
		sel_tags = revit.pick_elements()
		sel_tags = [i for i in sel_tags if i.GetType() == DB.IndependentTag]


def bend_tag_elbow(tag, angle):
	# DB.IndependentTag.LeaderEndCondition
	ref_tagged = DB.Reference(
				doc.GetElement(tag.TaggedLocalElementId))
	tag.HasLeader = True
	tag.LeaderEndCondition = DB.LeaderEndCondition.Free
	# pt1 = tag.LeaderEnd
	pt1 = tag.GetLeaderEnd(ref_tagged)
	pt2 = tag.TagHeadPosition

	new_z = pt2.Z
	delta_y = (pt2.Z - pt1.Z)/math.tan(math.radians(angle))
	if pt2.Y < pt1.Y:
		new_y = pt1.Y - delta_y
	else:
		new_y = pt1.Y + delta_y
	
	tag.SetLeaderElbow( ref_tagged, DB.XYZ(0, new_y, new_z) )


edited = 0
with revit.Transaction('Change Tags angle'):
	for tag in sel_tags:
		bend_tag_elbow(tag, angle)
		edited += 1
	
forms.alert('{} tags edit.'.format(edited), warn_icon=False)




