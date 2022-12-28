# -*- coding: utf-8 -*-
# Copyright (c) 2019, Jigar Tarpara and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


class ServiceRequestSetting(Document):
    pass


def setup_custom_fields():
    custom_fields = {
        "Item": [
            dict(fieldname='rental_item',
                 label='Rental Item',
                 fieldtype='Check',
                 insert_after='disabled',
                 print_hide=1),
            dict(fieldname='service_item',
                 label='Service Item',
                 fieldtype='Link',
                 insert_after='rental_item',
                 options='Item',
                 depends_on='eval:doc.rental_item',
                 read_only=0, print_hide=1),
            dict(fieldname='is_service_item',
                 label='Is Service Item',
                 fieldtype='Check',
                 insert_after='service_item',
                 options='Item',
                 depends_on='eval:!doc.rental_item',
                 read_only=0, print_hide=1)
        ],
        "Sales Order": [
            dict(fieldname='service_request',
                 label='Service Request',
                 fieldtype='Link',
                 insert_after='customer_name',
                 read_only=0,
                 options='Service Request'
                 ),
        ]
    }

    create_custom_fields(custom_fields)
    frappe.msgprint("Custom Field Updated!")