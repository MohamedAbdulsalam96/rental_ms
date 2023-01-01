
from frappe import _


def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on logs against this Vehicle. See timeline below for details'),
		'fieldname': 'vehicle_item',
		'non_standard_fieldnames':{
			'Delivery Trip': 'vehicle'
		},
		'transactions': [
			{
				'items': ['Vehicle Log']
			},
			{
				'items': ['Delivery Trip']
			}
		]
	}
