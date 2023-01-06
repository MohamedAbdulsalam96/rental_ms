// Copyright (c) 2023, Mohamed Abdulsalam Alqadasi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle', {
	refresh: function(frm) {
		frm.set_query("item_code", function(){
			return {
				filters: {
					"rental_item": 1
				}
			};
	});
    }

});
