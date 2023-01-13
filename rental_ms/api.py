import frappe
import json
import frappe.utils
from frappe import _
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html


@frappe.whitelist()
def make_supplier_quotation_for_default_supplier(source_name, selected_items=None, target_doc=None,supplier=None):
	"""Creates Supplier Quotation for each Supplier. Returns a list of doc objects."""
	if not selected_items:
		return

	if isinstance(selected_items, str):
		selected_items = json.loads(selected_items)

	def set_missing_values(source, target):
		target.supplier = supplier
		target.apply_discount_on = ""
		target.additional_discount_percentage = 0.0
		target.discount_amount = 0.0
		target.inter_company_order_reference = ""

		default_price_list = frappe.get_value("Supplier", supplier, "default_price_list")
		if default_price_list:
			target.buying_price_list = default_price_list

		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		# target.schedule_date = source.delivery_date
		target.qty = flt(source.qty)
		# target.stock_qty = flt(source.stock_qty) - flt(source.ordered_qty)
		# target.project = source_parent.project

	suppliers = [item.get("supplier") for item in selected_items if item.get("supplier")]
	suppliers = list(dict.fromkeys(suppliers))  # remove duplicates while preserving order

	items_to_map = [item.get("item_code") for item in selected_items if item.get("item_code")]
	items_to_map = list(set(items_to_map))

	if not suppliers:
		frappe.throw(
			_("Please set a Supplier against the Items to be considered in the Supplier Quotation.")
		)

	supplier_quotation = []
	for supplier in suppliers:
		doc = get_mapped_doc(
			"Opportunity",
			source_name,
			{
				"Opportunity": {
					"doctype": "Supplier Quotation",
					"field_no_map": [
						"address_display",
						"contact_display",
						"contact_mobile",
						"contact_email",
						"contact_person",
						"taxes_and_charges",
						"shipping_address",
						"terms",
					],
					"validation": {"status": ["!=","Lost"]},
				},
				"Opportunity Item": {
					"doctype": "Supplier Quotation Item",
					"field_map": [
						# ["name", "opportunity_item"],
						["parent", "opportunity"],
						# ["stock_uom", "stock_uom"],
						["uom", "uom"],
						# ["conversion_factor", "conversion_factor"],
						# ["delivery_date", "schedule_date"],
						["opportunity", "opportunity"]
					],
					"field_no_map": [
						"rate",
						"price_list_rate",
						"item_tax_template",
						"discount_percentage",
						"discount_amount",
						"pricing_rules",
					],
					"postprocess": update_item,
					"condition": lambda  doc: #doc.ordered_qty < doc.stock_qty
					 doc.supplier == supplier
					and doc.item_code in items_to_map,
				},
			},
			target_doc,
			set_missing_values,
		)

		doc.insert()
		frappe.db.commit()
		supplier_quotation.append(doc)

	return supplier_quotation

@frappe.whitelist()
def make_purchase_order_for_winner_items(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)

	doclist = get_mapped_doc(
		"Supplier Quotation",
		source_name,
		{
			"Supplier Quotation": {
				"doctype": "Purchase Order",
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Supplier Quotation Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "supplier_quotation_item"],
					["parent", "supplier_quotation"],
					["material_request", "material_request"],
					["material_request_item", "material_request_item"],
					["sales_order", "sales_order"],
				],
				"postprocess": update_item,
				"condition": lambda doc: doc.winner_item == 1,
			},
			"Purchase Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges",
			},
		},
		target_doc,
		set_missing_values,
	)

	doclist.set_onload("ignore_price_list", True)
	return doclist


# @frappe.whitelist()
# def make_supplier_quotation(source_name, selected_items=None, target_doc=None,rfq_supplier=None):
# 	if not selected_items:
# 		return

# 	if isinstance(selected_items, str):
# 		selected_items = json.loads(selected_items)

# 	def set_missing_values(source, target):
# 		target.supplier = rfq_supplier
# 		target.apply_discount_on = ""
# 		target.additional_discount_percentage = 0.0
# 		target.discount_amount = 0.0
# 		target.inter_company_order_reference = ""
# 		target.run_method("set_missing_values")
# 		target.run_method("calculate_taxes_and_totals")

# 	def update_item(source, target, source_parent):
# 		# target.schedule_date = source.delivery_date
# 		target.qty = flt(source.qty) - (flt(source.ordered_qty) / flt(source.conversion_factor))
# 		# target.stock_qty = flt(source.stock_qty) - flt(source.ordered_qty)
# 		# target.project = source_parent.project

# 	suppliers = [item.get("rfq_supplier") for item in selected_items if item.get("rfq_supplier")]
# 	suppliers = list(dict.fromkeys(suppliers))  # remove duplicates while preserving order

# 	items_to_map = [item.get("item_code") for item in selected_items if item.get("item_code")]
# 	items_to_map = list(set(items_to_map))

# 	if not suppliers:
# 		frappe.throw(
# 			_("Please set a Supplier against the Items to be considered in the Supplier Quotation.")
# 		)

# 	supplier_quotation = []
# 	for rfq_supplier in suppliers:
# 		doc = get_mapped_doc(
# 			"Opportunity",
# 			source_name,
# 			{
# 				"Opportunity": {
# 					"doctype": "Supplier Quotation",
# 					"field_no_map": [
# 						"address_display",
# 						"contact_display",
# 						"contact_mobile",
# 						"contact_email",
# 						"contact_person",
# 						"taxes_and_charges",
# 						"shipping_address",
# 						"terms",
# 					],
# 					"validation": {"status": ["!=","Lost"]},
# 				},
# 				"Opportunity Item": {
# 					"doctype": "Supplier Quotation Item",
# 					"field_map": [
# 						["name", "opportunity_item"],
# 						["parent", "opportunity"],
# 						# ["stock_uom", "stock_uom"],
# 						["uom", "uom"],
# 						# ["conversion_factor", "conversion_factor"],
# 						# ["delivery_date", "schedule_date"],
# 						["opportunity", "opportunity"],
# 					],
# 					"field_no_map": [
# 						"rate",
# 						"price_list_rate",
# 						"item_tax_template",
# 						"discount_percentage",
# 						"discount_amount",
# 						"pricing_rules",
# 					],
# 					"postprocess": update_item,
# 					"condition": lambda  doc: #doc.ordered_qty < doc.stock_qty
# 					doc.rfq_supplier == rfq_supplier
# 					and doc.item_code in items_to_map,
# 				},
# 			},
# 			target_doc,
# 			set_missing_values,
# 		)
		
# 		doc.insert()
# 		frappe.db.commit()
# 		supplier_quotation.append(doc)
# 		print("-------->",supplier_quotation)

# 	return supplier_quotation

