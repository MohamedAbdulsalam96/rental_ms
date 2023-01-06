// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Log", {
	refresh: function(frm) {
		frm.set_query("item", "claims", function(doc, cdt, cdn){
			return {
				filters: {
					"item_group": "Vehicle claims"
				}
			};
		});

		frm.trigger("add_toolbar_buttons"); 

		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Expense Claim'), function() {
				frm.events.expense_claim(frm);
			}, __('Create'));
			frm.page.set_inner_btn_group_as_primary(__('Create'));
		}
		// if(frm.doc.docstatus == 1){
		// 	cur_frm.add_custom_button(__('Sales Invoice'),
		// 		cur_frm.cscript['Make Sales Invoice'], __("Make"));
		// 	cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
		// }


	},

	// ////////////
	setup: function(frm) {
		frm.make_methods = {
			'Sales Invoice': function() { frm.trigger('create_sales_invoice') },
		}
	},
	add_toolbar_buttons: function(frm) {
		if(frm.doc.docstatus == 1){
			frappe.db.get_value("Sales Invoice", {"vehicle_log": frm.doc.name, "docstatus": 1}, "name", (r) => {
				if (Object.keys(r).length === 0) {
					frm.add_custom_button(__('Sales Invoice'), function() {
						frm.trigger('create_sales_invoice');
					},__('Create'))
				}
			});
	
		}

				
},
	create_sales_invoice: function(frm) {

		frappe.call({
			method: "rental_ms.rental_services_ms.doctype.vehicle_log.vehicle_log.create_sales_invoice_item",
			 		// rental_ms.rental_services_ms.doctype.vehicle_log.vehicle_log.create_pledge
			args: {
				vehicle_log: frm.doc.name
			},
			callback: function(r) {
				// var doc = frappe.model.sync(r.message);
				// frappe.set_route('Form', 'Sales Invoice', r.message.name);
				// frappe.set_route("Form", "Sales Invoice");
				// frappe.set_route("Form", "Sales Invoice", {"vehicle_log": frm.doc.name});
				frappe.set_route("Form", "Sales Invoice", {"doc.vehicle_log": frm.doc.name});
			}
		})
	},


	// ////////////

	expense_claim: function(frm){
		frappe.call({
			method: "erpnext.hr.doctype.vehicle_log.vehicle_log.make_expense_claim",
			args:{
				docname: frm.doc.name
			},
			callback: function(r){
				var doc = frappe.model.sync(r.message);
				frappe.set_route('Form', 'Expense Claim', r.message.name);
			}
		});
	}
});

cur_frm.cscript['Make Sales Invoice'] = function() {
	frappe.model.open_mapped_doc({
		method: "rental_ms.rental_services_ms.doctype.vehicle_log.vehicle_log.make_sales_invoice",
		frm: cur_frm
	})
};

frappe.ui.form.on('Claims Items', {
	item: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		cur_frm.call({
			"method": "frappe.client.get_value",
			"args": {
				"doctype": "Item",
				"filters": {
					"name":  child.item
				},
				"fieldname": "item_code"
			},
			"child": child,
			"fieldname": "item_code"
		})
		cur_frm.call({
			"method": "frappe.client.get_value",
			"args": {
				"doctype": "Item",
				"filters": {
					"name":  child.item
				},
				"fieldname": "image"
			},
			"child": child,
			"fieldname": "image",
			callback: function(r) {
				cur_frm.call({
					"method": "frappe.client.get_value",
					"args": {
						"doctype": "Item",
						"filters": {
							"name":  child.item
						},
						"fieldname": "stock_uom"
					},
					"child": child,
					"fieldname": "stock_uom",
					callback: function(r) {
						get_item_price_rate(frm, cdt, cdn);
						// calculate_qty(frm, cdt, cdn);
					}
				})	
			}
		})
		
	},
	// delivery_date: function(frm, cdt, cdn) {
	// 	calculate_qty(frm, cdt, cdn);
	// 	validate_booking_date(frm, cdt, cdn, "delivery_date");
	// },
	// return_date: function(frm, cdt, cdn) {
	// 	calculate_qty(frm, cdt, cdn);
	// 	validate_booking_date(frm, cdt, cdn, "return_date");
	// },
	rate: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		frappe.model.set_value(child.doctype, child.name, "amount", child.rate*child.quantity);
	}
})


var get_item_price_rate= function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];

	frappe.model.get_value('Item Price', 
		{
			'item_code': child.item_code,
			// 'price_list': "",
			'selling': 1
		}, 
		['price_list_rate', 'currency'], 
		function(d) {
			if(d) {
				frappe.model.set_value(child.doctype, child.name, "currency", d.currency);
				frappe.model.set_value(child.doctype, child.name, "rate", d.price_list_rate);
				
			}else{
				frappe.model.set_value(child.doctype, child.name, "rate", "0");
			}
		}
	)
}

// var calculate_qty= function(frm, cdt, cdn) {
// 	var child = locals[cdt][cdn];
// 	var diff = frappe.datetime.get_hour_diff(child.return_date,child.delivery_date);
// 	if(child.stock_uom == "Day"){
// 		diff = Math.ceil(diff/24);
// 	} 
// 	frappe.model.set_value(child.doctype, child.name, "quantity", diff);
// 	frappe.model.set_value(child.doctype, child.name, "amount", child.rate*child.quantity);
// }


