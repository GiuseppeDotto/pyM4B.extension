# Author:	Giuseppe Dotto

__doc__ =	"Report of all the pattern in the active document.\n\n"\
			"SHIFT-CLICK ●\nWill open a forms from which is possible "\
			"to select the patterns to delete."
__title__ = "Pattern\nReport ●"

from pyrevit import script, revit, DB, UI
output = script.get_output()
from pyrevit import PyRevitException, PyRevitIOError

from pyrevit import forms

doc = revit.doc

allMat = DB.FilteredElementCollector(doc).OfClass(DB.Material)
pattern_material = [m.SurfaceForegroundPatternId for m in allMat]
pattern_material += [m.SurfaceBackgroundPatternId for m in allMat]
pattern_material += [m.CutForegroundPatternId for m in allMat]
pattern_material += [m.CutBackgroundPatternId for m in allMat]

allFilledRegion = DB.FilteredElementCollector(doc).OfClass(DB.FilledRegionType).ToElements()
pattern_filledRegion = [f.ForegroundPatternId for f in allFilledRegion]
pattern_filledRegion += [f.BackgroundPatternId for f in allFilledRegion]

getName = lambda id: doc.GetElement(id).Name if id != DB.ElementId.InvalidElementId else None
pattern_material = set([getName(fp) for fp in pattern_material])
pattern_filledRegion = set([getName(fp) for fp in pattern_filledRegion])

pattern_all = DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement)
pattern_dict = dict(zip([fp.Name for fp in pattern_all], pattern_all))


if not __shiftclick__:
	header = ["Id", "PATTERN NAME", "USED IN MATERIAL", "USED IN FILLED REGION"]
	data = []
	for k in sorted(pattern_dict.keys()):
		if k in pattern_material and k in pattern_filledRegion:
			data.append( [output.linkify(pattern_dict[k].Id), k, 'X', 'X'] )
		elif k in pattern_material and k not in pattern_filledRegion:
			data.append( [output.linkify(pattern_dict[k].Id), k, 'X', ''] )
		elif k not in pattern_material and k in pattern_filledRegion:
			data.append( [output.linkify(pattern_dict[k].Id), k, '', 'X'] )
		else:
			data.append( [output.linkify(pattern_dict[k].Id), k, '', ''] )

	output.print_table(data, columns = header)

else:
	used, unused = [], []
	for k in pattern_dict.keys():
		if k in pattern_material or k in pattern_filledRegion:
			used.append(k)
		elif k in pattern_material and k in pattern_filledRegion:
			used.append(k)
		else:
			unused.append(k)
	ops = {"Unused":unused, "Used for Materials and/or FilledRegions":used}
	res = forms.SelectFromList.show(ops,
					multiselect=True,
					group_selector_title='Used/Unused Pattern Element',
					button_name='Delete Patterns')
	
	if res and forms.alert('Delete {} patterns?'.format(len(res)), yes=True, no=True):
		with revit.Transaction('Delete Patterns'):
			for k in res:
				doc.Delete(pattern_dict[k].Id)

