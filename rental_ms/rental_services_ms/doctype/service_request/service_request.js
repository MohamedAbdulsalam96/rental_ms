// Copyright (c) 2022, Mohamed Abdulsalam
// For license information, please see license.txt
// {% include 'rental_ms/rental_services_ms/loan_common.js' %};

frappe.ui.form.on('Service Request', {
	refresh: function(frm) {
		frm.set_query("item", "book_item", function(doc, cdt, cdn){
			return {
				filters: {
					"rental_item": 1
				}
			};
		});
		frm.set_query("item", function(){
			return {
				filters: {
					"rental_item": 1
				}
			};
			
		});
		// LP>>>>>>>
		frm.trigger("add_toolbar_buttons"); 
		  
		if(frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__('Sales Invoice'),
				cur_frm.cscript['Make Sales Invoice'], __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
		}

		if(frm.doc.docstatus == 1){
			cur_frm.add_custom_button(__('Vehicle Log'),
				cur_frm.cscript['Make Vehicle Log'], __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
		}		
	},
	setup: function(frm) {
		frm.make_methods = {
			'Loan Security Pledge': function() { frm.trigger('create_loan_security_pledge') },
		}
	},
	add_toolbar_buttons: function(frm) {
		if (frm.doc.is_secured_service) {
			frappe.db.get_value("Loan Security Pledge", {"service_request": frm.doc.name, "docstatus": 1}, "name", (r) => {
				if (Object.keys(r).length === 0) {
					frm.add_custom_button(__('Loan Security Pledge'), function() {
						frm.trigger('create_loan_security_pledge');
					},__('Create'))
				}
			});
		}
				
},
	create_loan_security_pledge: function(frm) {

		if(!frm.doc.is_secured_service) {
			frappe.throw(__("Loan Security Pledge can only be created for secured loans"));
		}

		frappe.call({
			method: "rental_ms.rental_services_ms.doctype.service_request.service_request.create_pledge",
			 		// rental_ms.rental_services_ms.doctype.service_request.service_request.create_pledge
			args: {
				service_request: frm.doc.name
			},
			callback: function(r) {
				frappe.set_route("Form", "Loan Security Pledge", r.message);
			}
		})
	},
	is_secured_service: function(frm) {
		frm.set_df_property('securities', 'reqd', frm.doc.is_secured_service);
	},

	calculate_amounts: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.qty) {
			frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.loan_security_price);
			frappe.model.set_value(cdt, cdn, 'post_haircut_amount', cint(row.amount - (row.amount * row.haircut/100)));
		} else if (row.amount) {
			frappe.model.set_value(cdt, cdn, 'qty', cint(row.amount / row.loan_security_price));
			frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.loan_security_price);
			frappe.model.set_value(cdt, cdn, 'post_haircut_amount', cint(row.amount - (row.amount * row.haircut/100)));
		}

		let maximum_amount = 0;

		$.each(frm.doc.securities || [], function(i, item){
			maximum_amount += item.post_haircut_amount;
		});

		if (flt(maximum_amount)) {
			frm.set_value('maximum_loan_amount', flt(maximum_amount));
		}

		let rental_items = "";

		$.each(frm.doc.book_item || [], function(i, item){
			rental_items = item.item;
		});

		if (rental_items) {
			frm.set_value('item', rental_items);
		}
	}
});

cur_frm.cscript['Make Sales Invoice'] = function() {
	frappe.model.open_mapped_doc({
		method: "rental_ms.rental_services_ms.doctype.service_request.service_request.make_sales_invoice",
		frm: cur_frm
	})
};

// *************************
// cur_frm.cscript['Make Vehicle Log']
cur_frm.cscript['Make Vehicle Log'] = function() {
	frappe.model.open_mapped_doc({
		method: "rental_ms.rental_services_ms.doctype.service_request.service_request.make_vehicle_log",
		frm: cur_frm
	})
};
// End: cur_frm.cscript['Make Vehicle Log']
// *****************************


frappe.ui.form.on('Service Request Item', {
	item: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		cur_frm.call({
			"method": "frappe.client.get_value",
			"args": {
				"doctype": "Item",
				"filters": {
					"name":  child.item
				},
				"fieldname": "service_item"
			},
			"child": child,
			"fieldname": "service_item"
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
							"name":  child.service_item
						},
						"fieldname": "stock_uom"
					},
					"child": child,
					"fieldname": "stock_uom",
					callback: function(r) {
						get_item_price_rate(frm, cdt, cdn);
						calculate_qty(frm, cdt, cdn);
					}
				})	
			}
		})
		
	},
	delivery_date: function(frm, cdt, cdn) {
		calculate_qty(frm, cdt, cdn);
		validate_booking_date(frm, cdt, cdn, "delivery_date");
	},
	return_date: function(frm, cdt, cdn) {
		calculate_qty(frm, cdt, cdn);
		validate_booking_date(frm, cdt, cdn, "return_date");
	},
	rate: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		frappe.model.set_value(child.doctype, child.name, "amount", child.rate*child.quantity);
	}
})

var get_item_price_rate= function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];

	frappe.model.get_value('Item Price', 
		{
			'item_code': child.service_item,
			'price_list': "البيع القياسي - YER",
			'selling': 1
		}, 
		'price_list_rate',
		function(d) {
			if(d) {
				frappe.model.set_value(child.doctype, child.name, "rate", d.price_list_rate);
			}else{
				frappe.model.set_value(child.doctype, child.name, "rate", "0");
			}
		}
	)
}

var calculate_qty= function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	var diff = frappe.datetime.get_hour_diff(child.return_date,child.delivery_date);
	if(child.stock_uom == "Day"){
		diff = Math.ceil(diff/24);
	} 
	frappe.model.set_value(child.doctype, child.name, "quantity", diff);
	frappe.model.set_value(child.doctype, child.name, "amount", child.rate*child.quantity);
}

var validate_booking_date = function(frm, cdt, cdn,  execution_point = "") {
	frappe.call({
		"method": "validate_booking_date",
		doc: cur_frm.doc,
		callback: function (r) {
			if(r.message){
				var child = locals[cdt][cdn];
				frappe.msgprint(r.message)
				frappe.model.set_value(child.doctype, child.name, execution_point,"");
			}	
		}
	})
}

// ******************************************
// From loan application

frappe.ui.form.on("Proposed Pledge", {
	loan_security: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		if (row.loan_security) {
			frappe.call({
				method: "rental_ms.rental_services_ms.doctype.service_request.service_request.get_loan_security_price",
				// method: "erpnext.loan_management.doctype.loan_security_price.loan_security_price.get_loan_security_price",
				args: {
					loan_security: row.loan_security
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, 'loan_security_price', r.message);
					frm.events.calculate_amounts(frm, cdt, cdn);
				}
			})
		}
	},

	amount: function(frm, cdt, cdn) {
		frm.events.calculate_amounts(frm, cdt, cdn);
	},

	qty: function(frm, cdt, cdn) {
		frm.events.calculate_amounts(frm, cdt, cdn);
	},
})
// ******************************************
// End : From loan application
















