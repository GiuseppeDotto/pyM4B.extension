# Author:	Giuseppe Dotto

__doc__ =	"Snoop through all the existent Journal files, looking for the operations "\
			"committed on the project having the specified name so to extract the active "\
			"working hours."

import os
from datetime import datetime
from pyrevit import revit, DB, script
from pyrevit import PyRevitException, PyRevitIOError

from pyrevit import forms
from rpw.ui.forms import (FlexForm, Label, TextBox,
							Separator, Button)

from System.Collections.Generic import List

doc = revit.doc

current_proj = doc.Title

# ASK FOR MODEL NAME
components = [Label('Project name:'),
			TextBox('textbox1', Text=current_proj),
			Separator(),
			Button('Select')]
form = FlexForm('Journal files - Spent huours', components)
form.show()

proj_name = form.values.get('textbox1')
if proj_name:
	proj_name = '[{}.rvt]'.format(proj_name)
	print('FILE NAME:\n'+proj_name)


	def group_operations(lines):
		out = []
		sub = []
		for i in lines:
			#if i.startswith('Jrn.'):
			if 'Jrn.Directive' in i:
				out.append(sub)
				sub = []
			sub.append(i.replace('\n', ''))
		return out

	def extract_data(txt):
		index = txt.index("'H")
		return	datetime.strptime( txt[index+3:index+23], '%d-%b-%Y %H:%M:%S' )


	localapp = os.getenv('LOCALAPPDATA')
	journal_path = os.path.join( localapp, 'Autodesk', 'Revit', doc.Application.VersionName, 'Journals')
	print('\nJOURNAL FILES LOCATION:\n' + journal_path)

	out = []
	days = []
	for root, dirs, files in os.walk(journal_path):
		for f in files:
			sub = []
			if 'journal' in f and f[-4:] == '.txt':
				file_name = os.path.join(root, f)

				with open(file_name, 'r') as j:
					lines = j.readlines()
					for gr in group_operations(lines):
						if proj_name in gr[1]:
							sub.append( extract_data(gr[-1]) )
			
			if sub:
				out.append(sub[-1] - sub[0])
				days.append(sub[0].strftime('%d-%b-%Y'))

	total_time = 'No time spent on the project.'
	if out:
		total_time = out[0]
		for t in out[1:]:	total_time += t
	
	print('\nTOTAL TIME:\n{}'.format(total_time))
	
	print( '\nDAILY ANALYSIS:' )
	for d, t in zip(days, out):
		print('{} : {}'.format(d, t))

