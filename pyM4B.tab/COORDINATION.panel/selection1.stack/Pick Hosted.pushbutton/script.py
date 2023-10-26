__doc__ =	"Select all the elements hosted to the selected element.\n"\
            "SHIFT-CLICK: Also the hosting element will be included in the selection."

__context__ = 'Selection'

from pyrevit import script, revit, DB, UI
from pyrevit import PyRevitException, PyRevitIOError
import clr
clr.AddReference('System')
from System.Collections.Generic import List

doc = revit.doc

hosted_ids = []
instance_filter = DB.ElementClassFilter(DB.FamilyInstance)
for elem in revit.get_selection():
    if __shiftclick__:
        hosted_ids += [elem.Id]
    hosted_ids += elem.GetDependentElements( instance_filter )

revit.uidoc.Selection.SetElementIds(List[DB.ElementId](hosted_ids))
