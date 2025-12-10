from . import __version__ as app_version

app_name = "smart_stock"
app_title = "Smart Stock"
app_publisher = "Your Company"
app_description = "Modern, easy-to-use stock management with visual controls, barcode support, and low stock alerts"
app_email = "your-email@example.com"
app_license = "MIT"

# Desk Pages - Main dashboard
desk_pages = ["stock-dashboard"]

# Document events
doc_events = {
    "Stock Entry": {
        "on_submit": "smart_stock.api.on_stock_entry_submit",
    },
    "Item": {
        "validate": "smart_stock.api.check_reorder_level",
    }
}

# Scheduled tasks for alerts
scheduler_events = {
    "daily": [
        "smart_stock.alerts.send_low_stock_alerts"
    ],
    "hourly": [
        "smart_stock.alerts.check_critical_stock"
    ]
}

# Custom fields to be added
after_install = "smart_stock.install.after_install"

# Override standard methods
# override_whitelisted_methods = {
#     "erpnext.stock.get_item_details.get_item_details": "smart_stock.api.get_item_details"
# }
