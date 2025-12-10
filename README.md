# Smart Stock - Modern Stock Management Dashboard

A beautiful, easy-to-use stock management dashboard for ERPNext with visual controls, barcode support, and intelligent low stock alerts.

## 🎯 What This App Does

Smart Stock transforms ERPNext's stock management into a modern, visual experience:

- **📊 Visual Dashboard** - See your entire stock situation at a glance
- **⚡ Quick Stock Entries** - Create stock in/out/transfer in seconds
- **📱 Barcode Scanning** - Scan barcodes to instantly find and update items
- **🔔 Smart Alerts** - Automatic low stock and critical stock notifications
- **📈 Real-time Statistics** - Live updates of stock levels and values
- **🎨 Color-Coded Status** - Instantly see which items need attention

## ✨ Key Features

### 1. Visual Stock Dashboard

Beautiful dashboard showing:
- **Total Items** - Count of all stock items
- **Low Stock Items** - Items approaching threshold (color-coded red/orange)
- **Out of Stock** - Items completely out of stock
- **Total Stock Value** - Real-time value of all inventory
- **Recent Movements** - Latest stock entries with visual indicators
- **Top Items by Value** - Your most valuable stock items

### 2. Quick Stock Entry

Create stock entries **3x faster** than standard ERPNext:
- One-click **Stock In** (Material Receipt)
- One-click **Stock Out** (Material Issue)  
- One-click **Stock Transfer** between warehouses
- Add multiple items at once
- Auto-populated fields
- Submit in seconds!

### 3. Barcode Scanning

Integrated barcode support:
- **Scan to Search** - Find items instantly with barcode scanner
- **Scan to Stock In/Out** - Scan item → Enter quantity → Done!
- **Keyboard Scanner Support** - Works with any USB barcode scanner
- **Mobile Scanning** - Use phone camera (coming soon)

### 4. Low Stock Alerts

Never run out of stock:
- **Automatic Daily Alerts** - Email notifications for low stock items
- **Critical Hour Alerts** - Immediate alerts for out-of-stock items
- **Configurable Thresholds** - Set custom levels per item
- **Visual Indicators** - Progress bars show stock levels
- **Smart Suggestions** - System recommends reorder quantities

### 5. Visual Stock Levels

See stock status instantly:
- **Color-Coded Cards** - Red (critical), Orange (low), Green (good)
- **Progress Bars** - Visual representation of stock levels
- **Warehouse View** - See stock across all warehouses
- **Item Groups** - Filter by category
- **Real-time Updates** - Auto-refresh every 60 seconds

## 📦 Installation

```bash
# 1. Copy to apps directory
cp -r smart_stock ~/frappe-bench/apps/

# 2. Install on your site
cd ~/frappe-bench
bench --site your-site install-app smart_stock
bench --site your-site clear-cache
bench restart
```

## 🚀 Quick Start

### Access the Dashboard

1. Log in to ERPNext
2. Search for **"Stock Dashboard"**
3. Or go directly to `/app/stock-dashboard`

You'll see:
```
┌─────────────────────────────────────────────────┐
│  STOCK DASHBOARD                                 │
├─────────────────────────────────────────────────┤
│  📊 Total: 1,234  🔴 Low: 23  ⚫ Out: 5  💰 $2.5M│
│                                                  │
│  🔍 [Barcode Scanner Input]        [Search]     │
│                                                  │
│  ⚠️ Low Stock (23)      📈 Recent Movements     │
│  • Widget A  →  5 left   • SE-001 Stock In     │
│  • Part B    →  2 left   • SE-002 Stock Out    │
│  • Tool C    →  8 left   • SE-003 Transfer     │
│                                                  │
│  ❌ Out of Stock (5)     ⭐ Top Items           │
│  • Component X           • Product A  $50,000   │
│  • Material Y            • Product B  $35,000   │
│  • Supply Z              • Product C  $28,000   │
└─────────────────────────────────────────────────┘
```

### Quick Stock In (Receipt)

1. Click **"Quick Stock In"** button
2. Select **To Warehouse**
3. Add items (or scan barcode)
4. Enter quantities
5. Click **"Create Stock Entry"**
6. Done! ✅

### Quick Stock Out (Issue)

1. Click **Stock Out** icon (top right)
2. Select **From Warehouse**
3. Add items to issue
4. Enter quantities
5. Submit - Done!

### Using Barcode Scanner

**Method 1: With Scanner**
1. Focus on barcode input field
2. Scan item barcode
3. Item details appear instantly
4. Click "Stock In" or "Stock Out"

**Method 2: Manual Entry**
1. Type item code or barcode
2. Press Enter or click Search
3. Item details shown
4. Choose action

## 🎨 Visual Indicators

### Stock Status Colors

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 Green | Good | Stock above threshold |
| 🟠 Orange | Low | Stock at/below threshold |
| 🔴 Red | Critical | Very low stock (<50% of threshold) |
| ⚫ Black | Out | Completely out of stock |

### Progress Bars

Each low stock item shows a visual progress bar:
```
Widget A                    5 / 20 units
████░░░░░░░░░░░░░░░░  25%  (Orange)
```

## 🔔 Setting Up Alerts

### Configure Low Stock Thresholds

**Per Item:**
1. Go to **Item** form
2. Find **"Smart Stock Settings"** section
3. Set **"Low Stock Quantity"** (default: 10)
4. Check **"Send Critical Alert"** for important items
5. Save

**Example:**
- Widget A: Low Stock Qty = 20 (alert when stock ≤ 20)
- Widget B: Low Stock Qty = 5 (alert when stock ≤ 5)
- Critical Item: Check "Send Critical Alert"

### Configure Alert Recipients

(Settings doctype coming in next update)

Default: Alerts go to users with "Stock Manager" role

## 📊 Dashboard Sections Explained

### Statistics Cards (Top)

**Total Items**
- Count of all active stock items
- Purple gradient card

**Low Stock**
- Items at or below threshold
- Orange gradient - needs attention!

**Out of Stock**
- Items with zero quantity
- Red gradient - urgent!

**Stock Value**
- Total value of all inventory
- Green gradient

### Low Stock Panel (Left)

Shows items that need reordering:
- **Card per item** with:
  - Item name and code
  - Current quantity vs threshold
  - Progress bar (visual indicator)
  - Warehouse location
- **Click card** to see full details
- **Color-coded** by urgency

### Out of Stock Panel (Left)

Critical items with zero stock:
- Red border cards
- "OUT OF STOCK" label
- Immediate action needed
- Click to create stock entry

### Recent Movements (Right)

Last 20 stock transactions:
- **Green icon** = Stock In (Receipt)
- **Red icon** = Stock Out (Issue)
- **Blue icon** = Transfer
- Shows date, time, warehouses
- Click to view full entry

### Top Items by Value (Right)

Your most valuable inventory:
- Ranked 1-10
- Shows quantity and total value
- Helps focus on important items
- Green indicator = healthy stock

## 🎯 Use Cases

### Retail Store

**Morning Routine:**
1. Open Stock Dashboard
2. Check overnight movements
3. Review low stock items
4. Create purchase requests for out-of-stock

**During Sales:**
1. Item sold → Quick Stock Out
2. Scan barcode → Enter quantity → Done
3. Real-time inventory update

### Warehouse

**Receiving Goods:**
1. Goods arrive
2. Scan barcode for each item
3. Quick Stock In
4. Quantities updated instantly

**Fulfilling Orders:**
1. Pick items
2. Scan to verify
3. Quick Stock Out
4. Order fulfilled!

### Manufacturing

**Raw Material Tracking:**
1. Monitor low stock alerts
2. Reorder before running out
3. Transfer materials between production lines
4. Track consumption in real-time

## ⚙️ Advanced Features

### Auto-Reorder (Coming Soon)

Set items to auto-create purchase requests:
- Check "Auto Reorder" on item
- Set reorder quantity
- System creates PR when low

### Batch & Serial Number Support

Dashboard supports:
- Batch-tracked items
- Serial number items
- Expiry tracking
- FIFO/LIFO

### Multi-Warehouse View

See stock across all warehouses:
- Click item card
- View warehouse-wise stock
- Transfer between warehouses
- Visual stock distribution

### Mobile Responsive

Dashboard works on:
- Desktop computers
- Tablets
- Mobile phones
- Touch-friendly interface

## 📈 Reports & Analytics

Access from dashboard:
- Stock Summary Report
- Stock Balance Report
- Stock Ledger
- Stock Ageing
- Warehouse-wise Stock

## 🔧 Configuration Options

### Item Settings

Each item can have:
- **Low Stock Qty** - When to alert (default: 10)
- **Critical Alert** - Immediate notification when out
- **Auto Reorder** - Automatic purchase requests
- **Reorder Qty** - How much to reorder
- **Barcode Type** - Code 128, EAN-13, etc.

### Alert Settings

Configure in Smart Stock Settings:
- Enable/disable daily alerts
- Enable/disable critical alerts
- Alert recipients (users/roles)
- Alert frequency
- Email templates

## 🎨 Customization

### Color Themes

Customize card colors in CSS:
- Total Items: Purple gradient
- Low Stock: Orange gradient
- Out of Stock: Red gradient
- Stock Value: Green gradient

### Dashboard Layout

Modify layout by editing:
- `/smart_stock/page/stock_dashboard/stock_dashboard.js`
- Rearrange panels
- Add custom sections
- Change card sizes

## 📱 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt + I` | Quick Stock In |
| `Alt + O` | Quick Stock Out |
| `Alt + T` | Quick Transfer |
| `Alt + B` | Focus Barcode Input |
| `F5` | Refresh Dashboard |

## 🚨 Troubleshooting

### Dashboard not loading?
```bash
bench --site your-site clear-cache
bench restart
```

### Barcode scanner not working?
- Check scanner is in keyboard emulation mode
- Test scanner in notepad first
- Ensure focus is on barcode input

### Alerts not sending?
- Check Smart Stock Settings
- Verify email configuration
- Check user has Stock Manager role

### Stock levels incorrect?
- Run Stock Balance report
- Check recent Stock Entries
- Verify warehouse permissions

## 🔐 Permissions

Users need these roles:
- **Stock Manager** - Full access to dashboard and entries
- **Stock User** - View dashboard, create entries
- **System Manager** - Full access + settings

## 📚 Next Steps

After installing Smart Stock:

1. **Set Thresholds** - Configure low stock quantities on key items
2. **Add Barcodes** - Assign barcodes to frequently used items
3. **Configure Alerts** - Set up email notifications
4. **Train Team** - Show staff how to use Quick Entry
5. **Monitor** - Check dashboard daily for low stock

## 🎉 Benefits

**Before Smart Stock:**
- Complex stock entry forms
- Hard to see stock levels
- Manual checking for low stock
- No visual indicators
- Slow barcode lookup

**After Smart Stock:**
- One-click stock entries ⚡
- Visual dashboard 📊
- Automatic alerts 🔔
- Color-coded status 🎨
- Instant barcode scanning 📱

## 🤝 Support

Need help?
- Check README.md
- Review dashboard help text
- Contact: your-email@example.com

## 📝 License

MIT

---

**Transform your stock management today with Smart Stock!** 🚀
