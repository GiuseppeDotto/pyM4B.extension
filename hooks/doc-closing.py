
from pyrevit import revit, forms, HOST_APP
import os
# import datetime

u_name = HOST_APP.username
# trigger = 'Jrn.Browser "LButtonDblClk"'
trigger = "Jrn.Activate "


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
						proj_name = row[row.index('[')+1 : row.index(']')]
						view_name = row[row.index(', "')+3 : -3]

						out.add( (u_name,
								proj_name,
								view_name,
								get_time(data[n-1])) )
	break


# WRITE CSV FILE
import csv

to_write = os.path.join(os.path.dirname(os.path.realpath(__file__)),
						'views usage.csv')
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


forms.alert('has been a wanderful adventure!')