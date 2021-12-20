
from pyrevit import revit, DB


# DETECTING ELEMENTS
accepted_classes = [DB.WallType, DB.FloorType,
					DB.CeilingType, DB.RoofType]
views_classes = [DB.ViewPlan, DB.ViewSection, DB.View3D]

def get_family(elem):

	if any( [elem.GetType() == x for x in accepted_classes] ):
		pass
	elif any( [elem.GetType() == x for x in views_classes] ):
		return	elem.Id
	elif elem.GetType() == DB.FamilySymbol:
		return	elem.Family.Id
	else:
		return	elem.Symbol.Family.Id

def get_type(elem):
	if any([elem.GetType() == x for x in accepted_classes]):
		return	elem.Id
	elif any( [elem.GetType() == x for x in views_classes] ):
		pass
	elif elem.GetType() == DB.Wall:
		return	elem.WallType.Id
	elif elem.GetType() == DB.FamilySymbol:
		return	elem.Id
	else:
		return	elem.Symbol.Id

# EDIT STRINGS
def to_PascalCase(current):
	new = ''
	for sub in current.split(' '):
		if len(sub) > 0:
			new += sub[0].upper() + sub[1:].lower()
	return	new

def add_prefix(current, prefix, toAdd):
	"""vw = string to edit
	prefix = prefix
	toAdd = Bool, (False:replace)
	"""
	if toAdd:
		return	prefix + current
	else:
		return	prefix + current[len(prefix):]