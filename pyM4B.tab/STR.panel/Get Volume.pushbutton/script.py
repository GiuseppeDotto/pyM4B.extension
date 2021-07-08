
__doc__ = 'Return the materials Volume of the selected element.'

from pyrevit import revit, DB, forms


with forms.WarningBar(title='pick soruce element'):
	elem = revit.pick_element('pick soruce element')


if elem:
	convert_v = lambda v: DB.UnitUtils.ConvertFromInternalUnits\
									(v, DB.DisplayUnitType.DUT_CUBIC_METERS)

	materials = elem.GetMaterialIds(False)

	msg = 'Materials and their volume:\n'
	for m_Id in materials:
		msg += '\n{} : {} m3'.format(revit.doc.GetElement(m_Id).Name,
								convert_v(elem.GetMaterialVolume(m_Id)))
	forms.alert(msg, warn_icon=False)
