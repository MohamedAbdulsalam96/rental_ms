# -*- coding: utf-8 -*-
# Copyright (c) 2018, Jigar Tarpara and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate, getdate
from frappe.model.document import Document


class ServiceRequest(Document):
	def validate(self):
		msg = self.validate_booking_date()
		if msg:
			frappe.throw(msg)

	@frappe.whitelist()
	def validate_booking_date(self):
		for row in self.book_item:
			is_booked = self.check_item_is_booked(row)
			if is_booked:
				return is_booked
		return ""

	def check_item_is_booked(self, row):
		delivery_date, return_date, item = row.delivery_date, row.return_date, row.item
		if delivery_date:
			filters = {}
			filters = {'item': item, 'docstatus': 1}

			filters.update({'delivery_date': ['<=', delivery_date]})
			filters.update({'return_date': ['>=', delivery_date]})
			filters.update({'docstatus': ['!=', 2]})
			filters.update({'name': ['!=', row.name]})

			bookings = frappe.get_all('Service Request Item', filters=filters, fields=[
									  'name', 'delivery_date', 'return_date', 'parent'])

			for booking in bookings:
				return "Already Booked: ID " + booking.parent

		if return_date:
			filters = {}
			filters = {'item': item, 'docstatus': 1}
			filters.update({'delivery_date': ['<=', return_date]})
			filters.update({'return_date': ['>=', return_date]})
			filters.update({'docstatus': ['!=', 2]})
			filters.update({'name': ['!=', row.name]})

			bookings = frappe.get_all('Service Request Item', filters=filters, fields=[
									  'name', 'delivery_date', 'return_date', 'parent'])

			for booking in bookings:
				return "Already Booked: ID " + booking.parent

		if delivery_date and return_date:

			filters = {}
			filters = {'item': item, 'docstatus': 1}
			filters.update({'name': ['!=', row.name]})
			filters.update(
				{'delivery_date': ['between', delivery_date+" and " + return_date]})

			bookings = frappe.get_all('Service Request Item', filters=filters, fields=[
									  'name', 'delivery_date', 'return_date', 'parent'])

			for booking in bookings:
				return "3 Already Booked: ID " + booking.parent + " \n" + str(filters)

			filters = {}
			filters = {'item': item, 'docstatus': 1}
			filters.update({'name': ['!=', row.name]})
			filters.update(
				{'return_date': ['between', delivery_date+" and " + return_date]})

			bookings = frappe.get_all('Service Request Item', filters=filters, fields=[
									  'name', 'delivery_date', 'return_date', 'parent'])

			for booking in bookings:
				return "Already Booked: ID " + booking.parent + " \n" + str(filters)

			if return_date < delivery_date:
				return "Return date should be after delivery date"

		return False


@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	cst = frappe.db.get_value("Service Request", source_name, ["customer"])
	customer = frappe.db.get_value("Customer", {"name": cst}, [
								   "name", "customer_name"], as_dict=True)

	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.quantity)
		target.qty = flt(obj.quantity)

	doclist = get_mapped_doc("Service Request", source_name, {
		"Service Request": {
			"doctype": "Sales Order",
			"field_map": {
				"parent": "service_request"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Service Request Item": {
			"doctype": "Sales Order Item",
			"field_map": {
				"service_item": "item_code",
				"quantity": "stock_qty",
				"quantity": "qty",
				"delivery_date": "delivery_date"
			},
			# "postprocess": update_item
		},
		"Sales Taxes and Charges": {
			"doctype": "Sales Taxes and Charges",
			"add_if_empty": True
		},
		"Sales Team": {
			"doctype": "Sales Team",
			"add_if_empty": True
		}
	}, target_doc, set_missing_values, ignore_permissions=True)

	# postprocess: fetch shipping address, set missing values

	return doclist


@frappe.whitelist()
def get_service_request_details(start, end, filters=None):
	events = []

	event_color = {
		0: "#ffdd9e",
		1: "#cdf5a6",
		2: "#8a0404"
	}

	from frappe.desk.reportview import get_filters_cond
	conditions = get_filters_cond("Service Request", filters, [])

	ServiceRequests = frappe.db.sql(""" SELECT `tabService Request`.name,`tabService Request`.docstatus, `tabService Request`.customer,
			ifnull(`tabService Request Item`.note, ''),
			min(`tabService Request Item`.delivery_date) as from_time,
			max(`tabService Request Item`.return_date) as to_time
		FROM `tabService Request` , `tabService Request Item`
		WHERE
			`tabService Request`.name = `tabService Request Item`.parent {0}
			group by `tabService Request`.name""".format(conditions), as_dict=1)

	for d in ServiceRequests:
		subject_data = []
		for field in ["name", "customer", "item", "note"]:
			if not d.get(field):
				continue

			subject_data.append(d.get(field))

		color = event_color.get(d.docstatus)
		# color = "#cdf5a6"
		job_card_data = {
			'from_time': d.from_time,
			'to_time': d.to_time,
			'name': d.name,
			'subject': '\n'.join(subject_data),
			'color': color if color else "#89bcde"
		}

		events.append(job_card_data)

	return events