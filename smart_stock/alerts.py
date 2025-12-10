import frappe
from frappe import _
from frappe.utils import now_datetime, cint

def send_low_stock_alerts():
    """
    Daily scheduled task to send low stock alerts.
    Sends email to configured users about items below threshold.
    """
    # TODO: Get settings from Smart Stock Settings doctype when created
    # For now, alerts are enabled by default
    enable_low_stock_alerts = True
    
    if not enable_low_stock_alerts:
        return
    
    # Get low stock items
    low_stock_items = frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            b.warehouse,
            b.actual_qty,
            COALESCE(NULLIF(i.custom_low_stock_qty, 0), 10) as threshold,
            i.stock_uom
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty > 0 
        AND b.actual_qty <= COALESCE(NULLIF(i.custom_low_stock_qty, 0), 10)
        AND i.is_stock_item = 1
        AND i.disabled = 0
        ORDER BY b.actual_qty ASC
    """, as_dict=True)
    
    if not low_stock_items:
        return
    
    # Build email content
    message = build_low_stock_email(low_stock_items)
    
    # Get recipients
    recipients = get_alert_recipients()
    
    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=_("Low Stock Alert - {0} Items Below Threshold").format(len(low_stock_items)),
            message=message,
            header=[_("Low Stock Alert"), "orange"]
        )
        
        # Log alert
        log_alert("Low Stock Alert", len(low_stock_items))


def check_critical_stock():
    """
    Hourly check for critical stock levels (out of stock).
    Sends immediate notification for items that just went out of stock.
    """
    # TODO: Get settings from Smart Stock Settings doctype when created
    # For now, critical alerts are enabled by default
    enable_critical_alerts = True
    
    if not enable_critical_alerts:
        return
    
    # Get out of stock items
    out_of_stock = frappe.db.sql("""
        SELECT 
            b.item_code,
            i.item_name,
            b.warehouse,
            i.stock_uom
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty <= 0
        AND i.is_stock_item = 1
        AND i.disabled = 0
        AND i.custom_critical_alert = 1
        LIMIT 50
    """, as_dict=True)
    
    if not out_of_stock:
        return
    
    # Build email content
    message = build_critical_stock_email(out_of_stock)
    
    # Get recipients
    recipients = get_alert_recipients()
    
    if recipients:
        frappe.sendmail(
            recipients=recipients,
            subject=_("CRITICAL: {0} Items Out of Stock").format(len(out_of_stock)),
            message=message,
            header=[_("Critical Stock Alert"), "red"]
        )
        
        # Log alert
        log_alert("Critical Stock Alert", len(out_of_stock))


def build_low_stock_email(items):
    """Build HTML email for low stock items."""
    
    html = """
    <h3 style="color: #f57c00;">Low Stock Alert</h3>
    <p>The following items are running low on stock:</p>
    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <thead>
            <tr style="background-color: #f5f5f5;">
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Item</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Warehouse</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Current Qty</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Threshold</th>
                <th style="padding: 10px; border: 1px solid #ddd;">UOM</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for item in items:
        html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">
                    <strong>{item.item_code}</strong><br>
                    <small>{item.item_name}</small>
                </td>
                <td style="padding: 10px; border: 1px solid #ddd;">{item.warehouse}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">
                    <span style="color: #f57c00; font-weight: bold;">{item.actual_qty}</span>
                </td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{item.threshold}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{item.stock_uom}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    <p style="margin-top: 20px;">
        <strong>Action Required:</strong> Please review and reorder these items as necessary.
    </p>
    """
    
    return html


def build_critical_stock_email(items):
    """Build HTML email for critical/out of stock items."""
    
    html = """
    <h3 style="color: #d32f2f;">CRITICAL: Out of Stock Alert</h3>
    <p>The following items are completely out of stock:</p>
    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <thead>
            <tr style="background-color: #ffebee;">
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Item</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Warehouse</th>
                <th style="padding: 10px; border: 1px solid #ddd;">UOM</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for item in items:
        html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">
                    <strong>{item.item_code}</strong><br>
                    <small>{item.item_name}</small>
                </td>
                <td style="padding: 10px; border: 1px solid #ddd;">{item.warehouse}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{item.stock_uom}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    <p style="margin-top: 20px; color: #d32f2f;">
        <strong>URGENT:</strong> These items require immediate attention!
    </p>
    """
    
    return html


def get_alert_recipients():
    """Get list of users who should receive stock alerts."""
    
    # TODO: Get recipients from Smart Stock Settings doctype when created
    # For now, default to Stock Manager role
    
    # Default: Send to users with Stock Manager role
    return frappe.db.sql_list("""
        SELECT DISTINCT parent 
        FROM `tabHas Role` 
        WHERE role = 'Stock Manager'
        AND parenttype = 'User'
        AND parent NOT IN ('Administrator', 'Guest')
    """)


def log_alert(alert_type, item_count):
    """Log alert for tracking."""
    
    # TODO: Create Stock Alert Log doctype and log alerts
    # For now, just log to console
    print(f"Alert sent: {alert_type} - {item_count} items")
    pass


@frappe.whitelist()
def send_test_alert():
    """Send a test alert email."""
    
    recipients = get_alert_recipients()
    
    if not recipients:
        frappe.throw(_("No alert recipients configured"))
    
    frappe.sendmail(
        recipients=recipients,
        subject=_("Test Alert from Smart Stock"),
        message="""
            <h3>Test Alert</h3>
            <p>This is a test alert from Smart Stock Management system.</p>
            <p>If you received this email, alerts are configured correctly!</p>
        """,
        header=[_("Test Alert"), "blue"]
    )
    
    return {"success": True, "message": _("Test alert sent to {0}").format(", ".join(recipients))}
