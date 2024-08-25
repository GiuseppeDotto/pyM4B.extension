
from pyrevit import DB, revit, forms,script
try: import DB
except: pass

doc = revit.doc

par_binding = doc.ParameterBindings
enum = par_binding.GetEnumerator()

parameters = dict()
while enum.MoveNext():
    is_shared = ''
    if 'shared' in enum.Key.GetTypeId().TypeId:
        is_shared = 'Shared'
    is_type = 'instance'
    if enum.Current.GetType() == DB.TypeBinding:
        is_type = 'type'
    name = enum.Key.Name
    props = ' - '.join([is_type, is_shared])
    parameters['[{}] {}'.format(props, name)] = enum.Key

par_keys = forms.SelectFromList.show(sorted(parameters.keys()),
                          multiselect=True,
                          button_name='Select Parameter to Delete')
if not par_keys: script.exit()
with revit.Transaction('M4B - Remove Project Parameters'):
    amount = 0
    for k in par_keys:
        doc.Delete(parameters[k].Id)
        amount += 1
forms.alert_ifnot(amount == 0,
                    '{} parameters successfully removed.'.format(amount))