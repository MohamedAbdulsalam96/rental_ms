# Copyright (c) 2023, Mohamed Abdulsalam
# For license information, please see license.txt
import frappe


def make_booking_service_item(doc, method):
    if doc.rental_item == 1:
        create_service_item(doc)
        validate_service_item(doc)


def create_service_item(item):
    if not frappe.db.exists("Item", item.item_code + "_RS"):
        service_request_setting = frappe.get_cached_doc("Service Request Setting")
        service_item = frappe.new_doc("Item")
        service_item.update({
            "item_code": item.item_code + "_RS",
            "item_name": item.item_name + "_RS",
            "item_group": service_request_setting.service_item_group,
            "stock_uom": service_request_setting.default_unit_of_measure,
            "is_stock_item": False,
            "is_service_item": True,
            "sandard_rate": "100"
        })
        service_item.save(ignore_permissions=True)
        item.service_item = service_item.name
    else:
        item.service_item = item.item_code + "_RS"
        print("item_name",item.item_name + " (R) ")
        frappe.db.set_value("Item",item.service_item, "item_name",item.item_name + " (R) ")
        frappe.db.set_value("Item",item.service_item, "image",item.image)

def validate_service_item(doc):
    if doc.service_item:
        is_service_item = frappe.db.get_value("Item",doc.service_item,"is_service_item")
        if not is_service_item:
            frappe.throw("Service Item must be checked Is Service Item.")
        is_stock_item = frappe.db.get_value("Item",doc.service_item,"is_stock_item")
        if is_stock_item:
            frappe.throw("Stock Item can't be use as service item.")

# ////////////////////////
def make_vehicle_item(doc, method):
    if doc.is_vehicle == 1:
        create_vehicle_item(doc)
        validate_vehicle_item(doc)

