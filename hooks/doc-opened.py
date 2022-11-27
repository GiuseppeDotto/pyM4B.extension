
from pyrevit import revit
# import os
# import datetime

doc = revit.doc


print(doc.Title)
print('----------------------')
with open(revit.get_current_journal_file(), 'r') as file:
	journal_file = file.readlines()[:]


for raw in journal_file:
	if "Jrn.Activate" in raw:
		print(raw)

# print('test')
# print(doc.ActiveView.Name)