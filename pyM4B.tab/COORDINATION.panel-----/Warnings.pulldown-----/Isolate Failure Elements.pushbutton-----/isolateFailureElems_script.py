# Author:	Giuseppe Dotto

__doc__ =	"The script will temporary isolate the elements reporting"\
			"the selected warning in the ACTIVE VIEW.\n"\
			"\n\n"\
			"From the list is possible to read the number of warnings (between '[]')"\
			"and their descriptions."


from pyrevit import revit, DB, UI
from pyrevit import PyRevitException, PyRevitIOError

from pyrevit import forms

from System.Collections.Generic import List

doc = revit.doc

allWarnings = doc.GetWarnings()

# CREATE LIST FROM WHICH SELECT WARNING
allNames = [w.GetDescriptionText() for w in allWarnings]
NameSet = list(set(allNames))
for i in range(len(NameSet)):
	nr = str( allNames.count(NameSet[i]) ).zfill(3)
	NameSet[i] = "[{}] ".format(nr) + NameSet[i]

NameSet = sorted(NameSet)[::-1]
NameSet = ["[{}] ALL".format(str(len(allNames)).zfill(3))]+NameSet

i = forms.SelectFromList.show(NameSet, title='select warning to isolate')
i = i[i.index(" ")+1:] # remove the number of occurencies from the name

# GET INTERESTED WARNINGS
intWarnings = [w for w in allWarnings if w.GetDescriptionText() == i]

# GET ALL FAILURE ELEMENTS
allElems = []
for w in intWarnings:
	allElems.extend(w.GetFailingElements())


with revit.Transaction('isolate failure elements'):
	vw = doc.ActiveView
	vw.IsolateElementsTemporary(List[DB.ElementId](allElems))

	# view.SetElementOverrides(id, overrideGraphicSetting)

