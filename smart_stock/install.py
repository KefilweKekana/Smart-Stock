import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """
    Run after app installation to set up custom fields and configurations.
    """
    print("Setting up Smart Stock...")
    
    # Create custom fields on Item
    create_item_custom_fields()
    
    # Create settings doctype if it doesn't exist
    # TODO: Create Smart Stock Settings doctype
    # create_default_settings()
    
    # Clear cache to ensure changes take effect
    frappe.clear_cache()
    
    print("Smart Stock setup completed successfully!")


def create_item_custom_fields():
    """
    Create custom fields on Item doctype for stock management.
    """
    custom_fields = {
        "Item": [
            {
                "fieldname": "custom_smart_stock_section",
                "label": "Smart Stock Settings",
                "fieldtype": "Section Break",
                "insert_after": "reorder_levels",
                "collapsible": 1
            },
            {
                "fieldname": "custom_low_stock_qty",
                "label": "Low Stock Quantity",
                "fieldtype": "Float",
                "insert_after": "custom_smart_stock_section",
                "description": "Alert when stock falls below this quantity (default: 10)",
                "default": "10"
            },
            {
                "fieldname": "custom_critical_alert",
                "label": "Send Critical Alert",
                "fieldtype": "Check",
                "insert_after": "custom_low_stock_qty",
                "description": "Send immediate alert when this item goes out of stock",
                "default": "0"
            },
            {
                "fieldname": "custom_barcode_type",
                "label": "Barcode Type",
                "fieldtype": "Select",
                "options": "Code 128\nCode 39\nEAN-13\nEAN-8\nUPC-A",
                "insert_after": "custom_critical_alert",
                "default": "Code 128"
            },
            {
                "fieldname": "custom_smart_stock_column",
                "fieldtype": "Column Break",
                "insert_after": "custom_barcode_type"
            },
            {
                "fieldname": "custom_auto_reorder",
                "label": "Auto Reorder",
                "fieldtype": "Check",
                "insert_after": "custom_smart_stock_column",
                "description": "Automatically create purchase request when low stock",
                "default": "0"
            },
            {
                "fieldname": "custom_reorder_qty",
                "label": "Auto Reorder Quantity",
                "fieldtype": "Float",
                "insert_after": "custom_auto_reorder",
                "depends_on": "eval:doc.custom_auto_reorder==1",
                "description": "Quantity to reorder automatically"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("Custom fields created successfully on Item!")


# Commented out - Settings doctype needs to be created first
# def create_default_settings():
#     """Create default Smart Stock Settings."""
#     
#     if not frappe.db.exists("Smart Stock Settings"):
#         settings = frappe.get_doc({
#             "doctype": "Smart Stock Settings",
#             "enable_low_stock_alerts": 1,
#             "enable_critical_alerts": 1,
#             "alert_frequency": "Daily",
#             "low_stock_threshold_default": 10
#         })
#         settings.insert(ignore_permissions=True)
#         frappe.db.commit()
#         print("Default settings created!")
