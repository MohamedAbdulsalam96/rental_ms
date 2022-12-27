frappe.ui.form.on('Item', {
    rental_item: function(frm) {
        if(frm.doc.rental_item == 0){
            frm.doc.service_item = ""
        }
    },
    onload: function(frm){
        frm.set_query("service_item", function() {
            return {
                "filters": {
                    "is_service_item": true,
                    "is_stock_item": false
                }
            };
        });
    }
})