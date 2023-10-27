
__doc__ = 'Create a report of all the used Revit view reading information from the journal files.\n'\
		'The information is stored in CSV format with a martrix whose columns are "USER, PROJECT, VIEW, DATE-TIME".'

from pyrevit import revit, forms, HOST_APP
import os
# import datetime

u_name = HOST_APP.username
# trigger = 'Jrn.Browser "LButtonDblClk"'
trigger = "Jrn.Close "


def get_time(s):
	if "'H " in s or "'E " in s:
		start = s.index('-')-2
		end = s.index('.')-3
		return	s[start:end]
	else:
		return '???'


out = set()
out.add(('USER', 'PROJECT', 'VIEW', 'DATE'))
for root, dirs, files in os.walk(revit.get_journals_folder()):
	for f in files:
		if '.txt' in f:
			with open( os.path.join(root, f), 'r' ) as journal:
				data = journal.readlines()[:]

				for n, row in enumerate(data):
					if trigger in row:
						proj_name = row.split('"')[1]
						view_name = row.split('"')[3]

						out.add( (u_name,
								proj_name,
								view_name,
								get_time(data[n-1])) )
	break


# WRITE CSV FILE
import csv
import datetime

now = datetime.datetime.today()
# to_write = os.path.join(os.path.dirname(os.path.realpath(__file__)),
# 						'views usage.csv')

dir_path = forms.pick_folder(title='Folder where to save Views History')
to_write = os.path.join(dir_path, 'pyM4B_ViewsHistory.csv')

			
if os.path.exists(to_write):
	with open(to_write, 'r') as csvfile:
		reader = csv.reader(csvfile)
		current = set()
		for r in reader:	current.add( (r[0], r[1], r[2], r[3]) )
	out = out | set(list(current)[1:])


out = sorted(list(out))
with open(to_write, 'wb') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerows(out)


forms.alert('View History successfully created!')