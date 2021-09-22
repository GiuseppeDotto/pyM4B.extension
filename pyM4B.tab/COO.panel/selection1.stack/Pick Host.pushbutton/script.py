__doc__ =	"Select the element which is hosting to the selected element.\n"\
            "SHIFT-CLICK: Also the hosted element will be included in the selection."

__context__ = 'Selection'

from pyrevit import script, revit, DB, UI
from pyrevit import PyRevitException, PyRevitIOError
import clr
clr.AddReference('System')
from System.Collections.Generic import List

doc = revit.doc

hosting_id = []
instance_filter = DB.ElementClassFilter(DB.FamilyInstance)
for elem in revit.get_selection():
    if __shiftclick__:
        hosting_id += [elem.Id]
    hosting_id += [elem.Host.Id]

revit.uidoc.Selection.SetElementIds(List[DB.ElementId](hosting_id))
