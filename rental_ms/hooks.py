from . import __version__ as app_version

app_name = "rental_ms"
app_title = "Rental Services MS"
app_publisher = "Mohamed Abdulsalam Alqadasi"
app_description = "Booking Any type of Service"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "moha2016it@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/rental_ms/css/rental_ms.css"
# app_include_js = "/assets/rental_ms/js/rental_ms.js"

# include js, css files in header of web template
# web_include_css = "/assets/rental_ms/css/rental_ms.css"
# web_include_js = "/assets/rental_ms/js/rental_ms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "rental_ms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}
doctype_js = {"Item" : "public/js/rental_ms_item.js"}
# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "rental_ms.install.before_install"
# after_install = "rental_ms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "rental_ms.uninstall.before_uninstall"
# after_uninstall = "rental_ms.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rental_ms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
    "Item": {
        "validate": "rental_ms.utils.make_booking_service_item"
    }
}
after_migrate = "rental_ms.rental_services_ms.doctype.service_request_setting.service_request_setting.setup_custom_fields"

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"rental_ms.tasks.all"
# 	],
# 	"daily": [
# 		"rental_ms.tasks.daily"
# 	],
# 	"hourly": [
# 		"rental_ms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rental_ms.tasks.weekly"
# 	]
# 	"monthly": [
# 		"rental_ms.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "rental_ms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "rental_ms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "rental_ms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"rental_ms.auth.validate"
# ]

