
__doc__ = 'Create a report of all the used Revit view reading information from the journal files.\n'\
        'The information is stored in CSV format with a martrix whose columns are "USER, PROJECT, VIEW, DATE-TIME".'

import os, csv
from pyrevit import HOST_APP, revit, forms


def txt_between(t, start, end):
    for x in t.split(start):
        if end in x:    return x[:x.index(end)]

user = HOST_APP.username


# Collect info from journals
trigger = '"ProjToPage"'
out = set()
out.add( ('USER', 'PROJECT', 'VIEW', 'DATE') )
search_time = False
for dirpath, dirnames, filenames in os.walk(revit.get_journals_folder()):
    for f in filenames:
        if 'journal.' in f and '.txt' in f:
            with open(os.path.join(dirpath, f), 'r') as journal:
                for row in journal.readlines():
                    if trigger in row:
                        sub = (user,
                               txt_between(row, '"[', ']"'),
                               txt_between(row, ', "', '"  _'))
                        search_time = True
                    elif search_time and "'H " in row:
                        if txt_between(row, "'H ", ' '):
                            sub += ("'"+txt_between(row, "'H ", ' '),)
                            out.add(sub)
                            search_time = False



# Store the new data in the CSV
dir_path = forms.pick_folder(title='Folder where to save Views History')
to_write = os.path.join(dir_path, 'pyM4B_ViewsHistory.csv')
csv_operation = 'created'

# Append data in case CSV is already existing
if os.path.exists(to_write):
    with open(to_write, 'r') as csvfile:
        reader = csv.reader(csvfile)
        current = set()
        for r in reader:	current.add( (r[0], r[1], r[2], r[3]) )
    out.remove(('USER', 'PROJECT', 'VIEW', 'DATE'))
    out = current | out
    csv_operation = 'updated'


out = sorted(list(out))
with open(to_write, 'wb') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(out)

forms.alert('View History CSV successfully {}!'.format(csv_operation),
            sub_msg=to_write)