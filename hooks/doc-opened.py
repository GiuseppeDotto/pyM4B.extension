
from pyrevit import revit, HOST_APP
import os
# import datetime


doc = revit.doc
u_name = HOST_APP.username

trigger = "GlobalToProj"
trigger = 'Jrn.Browser "LButtonDblClk"'
trigger = "ProjToPage"

def get_time(data, n):
	for j in range(1, 50):
		s = data[n+j]
		if "'H " in s or "'E " in s:
			start = s.index('-')-2
			end = s.index('.')-4
			return	s[start:end]
	return '???'


out = set()
for root, dirs, files in os.walk(revit.get_journals_folder()):
	for f in files:
		if '.txt' in f:
			with open( os.path.join(root, f), 'r' ) as journal:
				data = journal.readlines()[:]

				for n, i in enumerate(data):
					if trigger in i:
						out.add( (u_name,
									data[n].split('"')[-4],
									data[n].split('"')[-2],
									get_time(data, n)) )
	break


# for i in sorted(list(out)):
# 	print(i)

import csv

to_write = os.path.join(os.path.dirname(os.path.realpath(__file__)),
						'views usage.csv')
if os.path.exists(to_write):
	with open(to_write, 'r') as csvfile:
		reader = csv.reader(csvfile)
		current = set()
		for r in reader:	current.add( (r[0], r[1], r[2], r[3]) )
	out = out | current


out = sorted(list(out))
with open(to_write, 'wb') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerows(out)
	# for r in out:
	# 	writer.writerow(r)

# print(to_write)


# "GlobalToProj" , "[L05 - ActivityProject.rvt]" , "3D View: {3D}" _ 
#  'E 26-Nov-2022 15:11:40.295; 0:< 

# "GlobalToProj" , "[L05 - ActivityProject.rvt]" , "3D View: {3D}" _ 
#  'H 26-Nov-2022 15:14:46.698; 0:< 

