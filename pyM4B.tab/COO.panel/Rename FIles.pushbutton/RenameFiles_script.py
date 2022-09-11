__title__ = "Rename\nFiles"

__doc__ = "Rename all the files containing a Sheet Number in the "\
			"given folder according to Revit parameters.\n\n"\
			"The input is a string where is possible to specify "\
			"both [Sheet Parameters] and {Project Parameters}, by typing "\
			"the name of the parameter between the specific folder."

import os
import shutil
from datetime import datetime


from pyrevit import script, revit, DB, forms
from rpw.ui.forms import (FlexForm, Label, TextBox, CheckBox,\
						Separator, Button)


def find_between(txt, start, end):
	indices_start = [n for i,n in enumerate(txt) if i==start]
	indices_end = [n for i,n in enumerate(txt) if i==end]

	for s,e in zip(indices_start, indices_end):
		yield txt[s:e] +end

def get_par_value(par):
	if par.StorageType == DB.StorageType.String:
		return	par.AsString()
	else:
		return	par.AsValueString()

doc = revit.doc

# DEFINE FOLDER
dest_dir = forms.pick_folder('Pick folder with file to rename.')
forms.alert_ifnot(dest_dir, 'No folder selected.', exitscript=True)

# CREATE INPUT FORM
components = [Label('New name format:'),
			TextBox('textbox1', Text="M4B_{Project Parameter}_[Sheet Parameter]"),
			Separator(),
			CheckBox('archive', 'Create Archive', True),
			Separator(),
			Button('OK')]

form = FlexForm('Rename files in forlder', components)
form.show()
forms.alert_ifnot(form.values['textbox1'], 'No Name defined', exitscript=True)


# GET ALL SHEETS IN THE MODEL
all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType()
all_sheets = dict( [[s.SheetNumber, s] for s in all_sheets] )


proj_info = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ProjectInformation).FirstElement()


# define back-up folder
now = datetime.now()
archive_folder = now.strftime('%y%m%d - %H%M') + ' - Archive'
archive_folder = os.path.join(dest_dir, archive_folder)

for dirpath, dirnames, filenames in os.walk(dest_dir):
	filenames = [f for f in filenames if any([x in f for x in all_sheets.keys()])]
	for f in filenames:
		
		if form.values['archive']:
			shutil.copy2(os.path.join(dirpath, f), os.path.join(archive_folder, f))


		sheet = [s_nr for s_nr in all_sheets.keys() if s_nr in f]
		sheet = sorted(sheet, key=lambda n:len(n))[-1]
		sheet = all_sheets[sheet]
		# Replace Sheet Parameters
		for sh_par in find_between(f, '[', ']'):
			par = sheet.LookupParameter(sh_par[1:-1])
			forms.alert_ifnot(par, "{} parameter not recognized.".format(sh_par), exitscript=True)
			new_text = get_par_value(par)
			
			f.replace(sh_par, new_text)
		
		# Replace Project Parameter
		for pr_par in find_between(f, '{', '}'):
			par = proj_info.LookupParameter(pr_par[1:-1])
			forms.alert_ifnot(par, "{} parameter not recognized.".format(pr_par), exitscript=True)
			new_text = get_par_value(par)
			
			f.replace(pr_par, new_text)

		

		



