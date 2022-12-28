frappe.views.calendar['Service Request'] = {
	field_map: {
		start: 'from_time',
		end: 'to_time',
		id: 'name',
		allDay: 'allDay',
		title: 'subject',
		// status: 'event_type',
		color: 'color'
	},
	gantt: true,
	style_map: {
		Public: 'success',
		Private: 'info'
	},
	// order_by: 'to_time',
	get_events_method: 'rental_ms.rental_services_ms.doctype.service_request.service_request.get_service_request_details'
}