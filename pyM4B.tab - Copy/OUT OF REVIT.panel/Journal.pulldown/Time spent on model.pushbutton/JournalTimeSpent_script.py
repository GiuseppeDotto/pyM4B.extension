# Author:	Giuseppe Dotto

__doc__ =	"Snoop through all the existent Journal files, looking for the operations "\
			"committed on the project having the specified name so to extract the active "\
			"working hours."

import os
from itertools import groupby
from datetime import datetime, timedelta
from pyrevit import revit

from rpw.ui.forms import (FlexForm, Label, TextBox,
							Separator, Button)


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
	# proj_name = '{}.rvt'.format(proj_name)
	print('FILE NAME:\n'+proj_name)


	# DEFINITIONS
	get_model_name = lambda l: l[l.index('"[')+2 : l.index(']"')]
	get_time_string = lambda l: l[l.index("'")+3 : l.index(';')-4]
	to_datetime = lambda i: datetime.strptime( i, '%d-%b-%Y %H:%M:%S' )
	def collect_journalDirective(lines, proj_name):
		out = []
		for n, i in enumerate(lines):
			if 'Jrn.Directive' in i and '"[' in lines[n+1]:
				for j in range(20):
					if "'H " in lines[n+j] or "'E " in lines[n+j]:
						out.append([get_model_name(lines[n+1]),
									to_datetime(get_time_string(lines[n+j]))])
						break
		return	out
	
	def calculate_time(operations, proj_name):
		startTime = None
		all_deltas = []
		deltaTime = None
		for op in operations:
			if proj_name in op[0] and not startTime:
				startTime = op[1]
			elif proj_name in op[0] and startTime:
				deltaTime = op[1] - startTime
			elif proj_name not in op[0] and deltaTime:
				all_deltas.append([startTime.strftime('%d-%b-%Y'), deltaTime])
				startTime = None
				deltaTime = None

		for k, g in groupby(all_deltas, lambda x: x[0]):
			deltas = [i[1] for i in g]
			yield [k,
					len(deltas),
					sum(deltas, timedelta(0)) ]


	localapp = os.getenv('LOCALAPPDATA')
	journal_path = os.path.join( localapp, 'Autodesk', 'Revit', doc.Application.VersionName, 'Journals')
	print('\nJOURNAL FILES LOCATION:\n' + journal_path)


	operations = []
	for root, dirs, files in os.walk(journal_path):
		for f in files:
			sub = []
			if 'journal' in f and f[-4:] == '.txt':
				file_name = os.path.join(root, f)

				with open(file_name, 'r') as j:
					lines = j.readlines()
					operations.extend(collect_journalDirective(lines, proj_name))
	

	time_spent = list(calculate_time(operations, proj_name))

	if time_spent:
		print('\nTOTAL TIME:\n{}'.format(sum(zip(*time_spent)[-1], timedelta(0))))

		print( '\nTIME PER REVIT SESSION:' )
		for d, s, t in time_spent:
			print('{} : {} SESSIONS : {}'.format(d, s, t))


		print( "\n\nREMEMBER: Journal files collect data from users' Revit sessions on this computer, not from project's files." )

	else:
		print("\nNo time spent on the selected project.")
		
		print("\n PROJECTS VISIBLE FROM JOURNAL FILES:\n")
		for i in set(zip(*operations)[0]):
			print(i)