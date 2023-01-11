# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, getdate, cint, rounded, get_datetime
from frappe.model.mapper import get_mapped_doc


from six import string_types
import json
import math





class VehicleLog(Document):
	pass
	def validate(self):
		if flt(self.odometer) < flt(self.last_odometer):
			frappe.throw(_("Current Odometer Value should be greater than Last Odometer Value {0}").format(self.last_odometer))

	def on_submit(self):
		frappe.db.set_value("Vehicle", self.item_code, "last_odometer", self.odometer)

	def on_cancel(self):
		distance_travelled = self.odometer - self.last_odometer
		if(distance_travelled > 0):
			updated_odometer_value = int(frappe.db.get_value("Vehicle", self.item_code, "last_odometer")) - distance_travelled
			frappe.db.set_value("Vehicle", self.item_code, "last_odometer", updated_odometer_value)

@frappe.whitelist()
def make_expense_claim(docname):
	expense_claim = frappe.db.exists("Expense Claim", {"vehicle_log": docname})
	if expense_claim:
		frappe.throw(_("Expense Claim {0} already exists for the Vehicle Log").format(expense_claim))

	vehicle_log = frappe.get_doc("Vehicle Log", docname)
	service_expense = sum([flt(d.expense_amount) for d in vehicle_log.service_detail])

	claim_amount = service_expense + (flt(vehicle_log.price) * flt(vehicle_log.fuel_qty) or 1)
	if not claim_amount:
		frappe.throw(_("No additional expenses has been added"))

	exp_claim = frappe.new_doc("Expense Claim")
	exp_claim.employee = vehicle_log.employee
	exp_claim.vehicle_log = vehicle_log.name
	exp_claim.remark = _("Expense Claim for Vehicle Log {0}").format(vehicle_log.name)
	exp_claim.append("expenses", {
		"expense_date": vehicle_log.date,
		"description": _("Vehicle Expenses"),
		"amount": claim_amount
	})
	return exp_claim.as_dict()



# ///////// make_sales_invoice 
@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
	cst = frappe.db.get_value("Vehicle Log", source_name, ["customer"])
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

	doclist = get_mapped_doc("Vehicle Log", source_name, {
		"Vehicle Log": {
			"doctype": "Sales Invoice",
			"field_map": {
				"parent": "service_request",
				"service_request": "service_request"

			},
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Claims Item": {
			"doctype": "Sales Invoice Item",
			"field_map": {
				"item_code": "item",
				"stock_qty": "quantity",
				"qty": "quantity",



				# "item": "item_code",
				# "quantity": "stock_qty",
				# "quantity": "qty",
				# "delivery_date": "delivery_date"
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


	# //
@frappe.whitelist()
def create_sales_invoice_item(vehicle_log):
	vehicle_log_doc = frappe.get_doc("Vehicle Log", vehicle_log)

	lsp = frappe.new_doc("Sales Invoice")
	lsp.service_request = vehicle_log_doc.service_request
	lsp.vehicle_log = vehicle_log_doc.name
	lsp.customer = vehicle_log_doc.customer
	lsp.customer_name = vehicle_log_doc.customer
	# lsp.company = vehicle_log_doc.company

	# if loan:
	# 	lsp.loan = loan

	for claims in vehicle_log_doc.claims:

		lsp.append('items', {
			"item_code": claims.item,
			"qty": claims.quantity,
			"uom": claims.stock_uom,
			"rate": claims.rate
		})

	lsp.save()
	# lsp.submit()

	# message = _("Sales Invoice Created : {0}").format(lsp.name)
	# frappe.msgprint(message)


	

