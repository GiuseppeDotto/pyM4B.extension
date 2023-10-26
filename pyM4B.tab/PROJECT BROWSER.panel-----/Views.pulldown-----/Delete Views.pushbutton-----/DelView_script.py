# Author:	Giuseppe Dotto

__doc__ =	"Delete multiple views at a time, selecting them through their name."\
			"Active view can't be deleted."

from pyrevit import revit, DB, UI, script
from pyrevit import PyRevitException, PyRevitIOError
from pyrevit import forms

from rpw.ui.forms import (FlexForm, Label, ComboBox, TextBox, TextBox,
							Separator, Button, CheckBox)

from itertools import groupby

def getValue(p):
	if not p:
		return	None
	elif p.StorageType == DB.StorageType.Integer:
		return	p.AsInteger()
	elif p.StorageType == DB.StorageType.Double:
		return	p.AsDouble()
	elif p.StorageType == DB.StorageType.String:
		return	p.AsString()
	elif p.StorageType == DB.StorageType.ElementId:
		return	p.AsValueString()

def exclude_activeView(views, activeV):
	out = []
	for v in views:
		if v.Id == activeV.Id:
			forms.alert("Active view can't be deleted.")
		else:
			out.append(v)
	return	out

doc = revit.doc

BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter

collector = DB.FilteredElementCollector

allViewClass = collector(doc).OfClass(DB.View)
_views = [v for v in allViewClass if not v.IsTemplate]

name_vw = sorted( [[v.Name, v] for v in _views] )
_views = zip(*name_vw)[1]

params = sorted([p.Definition.Name for p in _views[0].Parameters])

# MAKE FORMS
components = [Label('Pick Parameter to group the views:'),
			ComboBox('combobox1', params),
			CheckBox('checkbox1', 'Group by the parameter above'),
			Separator(),
			CheckBox('checkbox2', 'Exclude views on sheets'),
			CheckBox('checkbox3', 'Exclude parent views with dependent'),
			Separator(),
			Button('Select')]
form = FlexForm('Delete Views by Name - Options', components)
form.show()

if not form.values: script.exit()

if form.values["checkbox2"]:
	_views = [v for v in _views
		if v.Parameter[BIP.VIEWPORT_SHEET_NAME].AsString() == None]
if form.values["checkbox3"]:
	_views = [v for v in _views
		if len(v.GetDependentViewIds()) == 0]
if form.values["checkbox1"]:
	pName = form.values["combobox1"]
	temp = sorted([[getValue(v.LookupParameter(pName)), v] for v in _views])
	_views_dict = dict()
	for k, g in groupby(temp, lambda x:x[0]):
		_views_dict[k] = [s[1] for s in g]
	_views = _views_dict
		
toDel = forms.SelectFromList.show(_views, title = "select views to delete",\
							multiselect=True, name_attr='Name')


if not toDel:	script.exit()
elif forms.alert("delete {} views?".format(len(toDel)), yes = True, no = True):
	toDel = [v for v in toDel if v.IsValidObject]
	toDel = exclude_activeView(toDel, doc.ActiveView)
	if toDel:
		count = 0
		with revit.Transaction("Deleted {} Views".format(len(toDel))):
			with forms.ProgressBar(title='Deleting Views') as pb:
				for vw in toDel:
					try:	doc.Delete(vw.Id)
					except:	pass
					count += 1
					pb.update_progress(count, len(toDel))
