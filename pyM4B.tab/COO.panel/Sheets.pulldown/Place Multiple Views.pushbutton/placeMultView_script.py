
__doc__ = 'Place multiple views at the same time. '\
			'The views will be placed without any specific layout.'

from pyrevit import script, revit, DB, forms

BIP = DB.BuiltInParameter

def get_y_dimension(vp):
	y = vp.GetBoxOutline().MaximumPoint.Y - vp.GetBoxOutline().MinimumPoint.Y
	if y < 0:
		return  -y
	else:
		return  y

# GET VIEWS
views = forms.select_views(title='Select Views', button_name='Select', 
					multiple=True, use_selection=True)
if not views:   script.exit()

sheet = forms.select_sheets(title='Select Sheets', button_name='Select', multiple=False)
if not sheet:   script.exit()


# PLACE VIEWS
with forms.ProgressBar(title='Place Multiple Views') as pb:
	nr = 0
	pb.update_progress(nr, len(views))
	with revit.Transaction('Place Multiple View'):
		pt = DB.XYZ()
		for vw in views:
			if vw.Parameter[BIP.VIEWER_SHEET_NUMBER].AsString() == '---':
				vp = DB.Viewport.Create(revit.doc, sheet.Id, vw.Id, pt)

				pt = pt.Subtract(DB.XYZ(0, get_y_dimension(vp), 0))
				nr += 1
				pb.update_progress(nr, len(views))