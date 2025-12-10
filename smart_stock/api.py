import frappe
from frappe import _
from frappe.utils import flt, now, today, add_days, cint
import json

@frappe.whitelist()
def get_stock_dashboard_data():
    """
    Get comprehensive stock dashboard data.
    Returns stock levels, alerts, statistics, and recent movements.
    """
    data = {
        "statistics": get_stock_statistics(),
        "low_stock_items": get_low_stock_items(limit=10),
        "out_of_stock_items": get_out_of_stock_items(limit=10),
        "recent_movements": get_recent_stock_movements(limit=20),
        "stock_by_warehouse": get_stock_by_warehouse(),
        "top_items": get_top_items_by_value(limit=10)
    }
    
    return data


def get_stock_statistics():
    """Get overall stock statistics."""
    
    # Total items
    total_items = frappe.db.count('Item', {'is_stock_item': 1, 'disabled': 0})
    
    # Items in stock
    items_in_stock = frappe.db.sql("""
        SELECT COUNT(DISTINCT item_code)
        FROM `tabBin`
        WHERE actual_qty > 0
    """)[0][0] or 0
    
    # Low stock items
    low_stock = frappe.db.sql("""
        SELECT COUNT(DISTINCT b.item_code)
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty > 0 
        AND b.actual_qty <= COALESCE(NULLIF(i.custom_low_stock_qty, 0), 10)
        AND i.is_stock_item = 1
        AND i.disabled = 0
    """)[0][0] or 0
    
    # Out of stock
    out_of_stock = frappe.db.sql("""
        SELECT COUNT(DISTINCT b.item_code)
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty <= 0
        AND i.is_stock_item = 1
        AND i.disabled = 0
    """)[0][0] or 0
    
    # Total stock value
    total_value = frappe.db.sql("""
        SELECT SUM(b.actual_qty * b.valuation_rate)
        FROM `tabBin` b
        WHERE b.actual_qty > 0
    """)[0][0] or 0
    
    return {
        "total_items": total_items,
        "items_in_stock": items_in_stock,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_value": flt(total_value, 2)
    }


@frappe.whitelist()
def get_low_stock_items(limit=50, warehouse=None):
    """Get items with low stock levels."""
    
    warehouse_condition = ""
    if warehouse:
        warehouse_condition = f"AND b.warehouse = '{warehouse}'"
    
    items = frappe.db.sql(f"""
        SELECT 
            b.item_code,
            i.item_name,
            i.item_group,
            b.warehouse,
            b.actual_qty,
            COALESCE(NULLIF(i.custom_low_stock_qty, 0), 10) as threshold,
            b.valuation_rate,
            i.stock_uom,
            i.image
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty > 0 
        AND b.actual_qty <= COALESCE(NULLIF(i.custom_low_stock_qty, 0), 10)
        AND i.is_stock_item = 1
        AND i.disabled = 0
        {warehouse_condition}
        ORDER BY b.actual_qty ASC
        LIMIT {limit}
    """, as_dict=True)
    
    return items


@frappe.whitelist()
def get_out_of_stock_items(limit=50, warehouse=None):
    """Get items that are out of stock."""
    
    warehouse_condition = ""
    if warehouse:
        warehouse_condition = f"AND b.warehouse = '{warehouse}'"
    
    items = frappe.db.sql(f"""
        SELECT 
            b.item_code,
            i.item_name,
            i.item_group,
            b.warehouse,
            b.actual_qty,
            i.stock_uom,
            i.image
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty <= 0
        AND i.is_stock_item = 1
        AND i.disabled = 0
        {warehouse_condition}
        ORDER BY i.item_name
        LIMIT {limit}
    """, as_dict=True)
    
    return items


@frappe.whitelist()
def get_recent_stock_movements(limit=20):
    """Get recent stock entry transactions."""
    
    movements = frappe.db.sql("""
        SELECT 
            se.name,
            se.stock_entry_type,
            se.posting_date,
            se.posting_time,
            se.total_outgoing_value,
            se.total_incoming_value,
            se.from_warehouse,
            se.to_warehouse,
            se.owner
        FROM `tabStock Entry` se
        WHERE se.docstatus = 1
        ORDER BY se.posting_date DESC, se.posting_time DESC
        LIMIT %s
    """, limit, as_dict=True)
    
    return movements


@frappe.whitelist()
def get_stock_by_warehouse():
    """Get stock value grouped by warehouse."""
    
    warehouses = frappe.db.sql("""
        SELECT 
            b.warehouse,
            COUNT(DISTINCT b.item_code) as item_count,
            SUM(b.actual_qty) as total_qty,
            SUM(b.actual_qty * b.valuation_rate) as total_value
        FROM `tabBin` b
        WHERE b.actual_qty > 0
        GROUP BY b.warehouse
        ORDER BY total_value DESC
    """, as_dict=True)
    
    return warehouses


@frappe.whitelist()
def get_top_items_by_value(limit=10):
    """Get top items by stock value."""
    
    items = frappe.db.sql(f"""
        SELECT 
            b.item_code,
            i.item_name,
            i.item_group,
            SUM(b.actual_qty) as total_qty,
            AVG(b.valuation_rate) as avg_rate,
            SUM(b.actual_qty * b.valuation_rate) as total_value,
            i.stock_uom
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty > 0
        AND i.is_stock_item = 1
        GROUP BY b.item_code
        ORDER BY total_value DESC
        LIMIT {limit}
    """, as_dict=True)
    
    return items


@frappe.whitelist()
def search_item_by_barcode(barcode):
    """Search for an item using barcode."""
    
    if not barcode:
        return None
    
    # Try item barcode
    item = frappe.db.get_value("Item Barcode", {"barcode": barcode}, "parent")
    
    if item:
        return get_item_details(item)
    
    # Try item code directly
    if frappe.db.exists("Item", barcode):
        return get_item_details(barcode)
    
    return None


@frappe.whitelist()
def get_item_details(item_code, warehouse=None):
    """Get detailed information about an item including stock levels."""
    
    item = frappe.get_doc("Item", item_code)
    
    # Get stock balance
    stock_balance = []
    if warehouse:
        bal = frappe.db.get_value("Bin", 
            {"item_code": item_code, "warehouse": warehouse},
            ["actual_qty", "valuation_rate"], as_dict=True)
        if bal:
            stock_balance.append({
                "warehouse": warehouse,
                "actual_qty": bal.actual_qty,
                "valuation_rate": bal.valuation_rate
            })
    else:
        stock_balance = frappe.db.sql("""
            SELECT warehouse, actual_qty, valuation_rate
            FROM `tabBin`
            WHERE item_code = %s AND actual_qty != 0
        """, item_code, as_dict=True)
    
    return {
        "item_code": item.name,
        "item_name": item.item_name,
        "item_group": item.item_group,
        "stock_uom": item.stock_uom,
        "image": item.image,
        "has_batch_no": item.has_batch_no,
        "has_serial_no": item.has_serial_no,
        "description": item.description,
        "stock_balance": stock_balance,
        "total_qty": sum([d.actual_qty for d in stock_balance]),
        "barcodes": [d.barcode for d in item.barcodes] if item.barcodes else []
    }


@frappe.whitelist()
def create_quick_stock_entry(entry_type, items, from_warehouse=None, to_warehouse=None, remarks=None):
    """
    Create a stock entry quickly.
    
    Args:
        entry_type: Material Receipt, Material Issue, or Material Transfer
        items: List of items with item_code, qty, and optionally warehouse
        from_warehouse: Source warehouse (for Issue/Transfer)
        to_warehouse: Target warehouse (for Receipt/Transfer)
        remarks: Optional remarks
    """
    if isinstance(items, str):
        items = json.loads(items)
    
    # Create stock entry
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = entry_type
    se.company = frappe.defaults.get_user_default("Company")
    
    if from_warehouse:
        se.from_warehouse = from_warehouse
    if to_warehouse:
        se.to_warehouse = to_warehouse
    if remarks:
        se.remarks = remarks
    
    # Add items
    for item_data in items:
        se.append("items", {
            "item_code": item_data.get("item_code"),
            "qty": flt(item_data.get("qty")),
            "s_warehouse": from_warehouse or item_data.get("s_warehouse"),
            "t_warehouse": to_warehouse or item_data.get("t_warehouse"),
            "batch_no": item_data.get("batch_no"),
            "serial_no": item_data.get("serial_no"),
        })
    
    se.insert()
    se.submit()
    
    return {
        "success": True,
        "stock_entry": se.name,
        "message": _("Stock Entry {0} created successfully").format(se.name)
    }


@frappe.whitelist()
def get_item_stock_levels(item_code):
    """Get stock levels for an item across all warehouses."""
    
    levels = frappe.db.sql("""
        SELECT 
            b.warehouse,
            w.warehouse_name,
            b.actual_qty,
            b.reserved_qty,
            b.ordered_qty,
            b.planned_qty,
            b.valuation_rate,
            (b.actual_qty * b.valuation_rate) as stock_value
        FROM `tabBin` b
        LEFT JOIN `tabWarehouse` w ON b.warehouse = w.name
        WHERE b.item_code = %s
        ORDER BY b.actual_qty DESC
    """, item_code, as_dict=True)
    
    return levels


@frappe.whitelist()
def set_low_stock_threshold(item_code, threshold):
    """Set low stock threshold for an item."""
    
    frappe.db.set_value("Item", item_code, "custom_low_stock_qty", flt(threshold))
    frappe.db.commit()
    
    return {"success": True, "message": _("Threshold updated")}


def on_stock_entry_submit(doc, method):
    """Hook called when stock entry is submitted."""
    # Could trigger notifications, webhooks, etc.
    pass


def check_reorder_level(doc, method):
    """Check if item needs reordering."""
    # Implement reorder logic
    pass


@frappe.whitelist()
def get_warehouses():
    """Get list of warehouses."""
    return frappe.get_all("Warehouse", 
        filters={"is_group": 0, "disabled": 0},
        fields=["name", "warehouse_name"],
        order_by="warehouse_name")


@frappe.whitelist()
def get_stock_summary(filters=None):
    """Get stock summary with filters."""
    
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    conditions = ["i.is_stock_item = 1", "i.disabled = 0"]
    values = []
    
    if filters:
        if filters.get("item_group"):
            conditions.append("i.item_group = %s")
            values.append(filters["item_group"])
        
        if filters.get("warehouse"):
            conditions.append("b.warehouse = %s")
            values.append(filters["warehouse"])
        
        if filters.get("stock_status"):
            if filters["stock_status"] == "in_stock":
                conditions.append("b.actual_qty > 0")
            elif filters["stock_status"] == "low_stock":
                conditions.append("b.actual_qty > 0")
                conditions.append("b.actual_qty <= COALESCE(NULLIF(i.custom_low_stock_qty, 0), 10)")
            elif filters["stock_status"] == "out_of_stock":
                conditions.append("b.actual_qty <= 0")
    
    where_clause = " AND ".join(conditions)
    
    items = frappe.db.sql(f"""
        SELECT 
            i.name as item_code,
            i.item_name,
            i.item_group,
            i.stock_uom,
            i.image,
            b.warehouse,
            b.actual_qty,
            b.valuation_rate,
            (b.actual_qty * b.valuation_rate) as stock_value,
            COALESCE(NULLIF(i.custom_low_stock_qty, 0), 10) as low_stock_threshold
        FROM `tabItem` i
        LEFT JOIN `tabBin` b ON i.name = b.item_code
        WHERE {where_clause}
        ORDER BY i.item_name
        LIMIT 500
    """, tuple(values), as_dict=True)
    
    return items
