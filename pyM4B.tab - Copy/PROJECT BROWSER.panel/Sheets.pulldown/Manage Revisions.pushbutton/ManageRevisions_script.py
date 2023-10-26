
__doc__ = 'Set/Add/Remove Revisions for multiple sheets.\n\n'\
			'- Set: replace the current revision set with the given one.\n'\
			'- Add: Add the selected revision the current revision.\n'\
			'- Remove: Remove the selected revision the current revision.\n'


from pyrevit import script, revit, DB, forms
from rpw.utils.dotnet import List

# USER INTENTION
ops = ['Set', 'Add', 'Remove']
operation = forms.CommandSwitchWindow.show(ops, message='Select Operation')
if not operation:   script.exit()

# GET REVISIONS
revisions = forms.select_revisions(multiple=True)
if not revisions:   script.exit()

sheets = forms.select_sheets(title='Select Sheets', button_name='Select', multiple=True)
if not sheets:   script.exit()



# MANAGE REVISIONS
revisions = [r.Id for r in revisions]
with forms.ProgressBar(title='Edit Sheet revisions') as pb:
	nr = 0
	pb.update_progress(nr, len(sheets))
	with revit.Transaction('Edit Sheet revisions'):
		
		for sheet in sheets:
			if operation == 'Set':
				sheet.SetAdditionalRevisionIds(List[DB.ElementId](revisions))

			elif operation == 'Add':							
				x = sheet.GetAllRevisionIds()
				sheet.SetAdditionalRevisionIds(List[DB.ElementId](revisions+list(x)))

			elif operation == 'Remove':
				x = sheet.GetAllRevisionIds()
				x = [i for i in x if i not in revisions]
				sheet.SetAdditionalRevisionIds(List[DB.ElementId](x))
			
			nr += 1
			pb.update_progress(nr, len(sheets))
