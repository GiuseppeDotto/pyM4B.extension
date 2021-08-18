# Author:	Giuseppe Dotto

__doc__ =	"Shows all the Titleblocks used in each project's sheets."

from pyrevit import script, revit, DB
output = script.get_output()
from pyrevit import PyRevitException, PyRevitIOError


doc = revit.doc

BIC = DB.BuiltInCategory
BIP = DB.BuiltInParameter
tb_name = lambda t: t.Parameter[BIP.ELEM_FAMILY_AND_TYPE_PARAM].AsValueString()
tb_workset = lambda tb: tb.Parameter[BIP.ELEM_PARTITION_PARAM].AsValueString().replace('View "Sheet: ', '')[:-1]

collector = DB.FilteredElementCollector
all_tb = collector(doc).OfCategory(BIC.OST_TitleBlocks).WhereElementIsNotElementType()

# GET UNUSED TITLEBLOCK
all_tb_type_used = set([tb.GetTypeId() for tb in all_tb])
all_tb_type = collector(doc).OfCategory(BIC.OST_TitleBlocks).WhereElementIsElementType()
all_tb_type = set([tb.Id for tb in all_tb_type])
all_tb_type_unused = all_tb_type - all_tb_type_used

# COLLECT DATA
data = [[tb_workset(tb), tb_name(tb)] for tb in all_tb]

# PRINT RESULTS
report_title = 'Count of Titleblocks: {}\nCount of Titleblock Types: {}\n\n'\
				'Used Types: {}\nUnused Types: {}\n'.format(len(data), len(all_tb_type),
				len(all_tb_type_used), len(all_tb_type_unused))

print(report_title)

header = ["SHEETS NAME", "TITLEBLOCKS NAME"]
output.print_table(sorted(data), columns = header)
