frappe.pages['stock-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Stock Dashboard'),
		single_column: false
	});

	new StockDashboard(page);
};

class StockDashboard {
	constructor(page) {
		this.page = page;
		this.parent = $(page.body);
		this.barcode_buffer = '';
		this.barcode_timeout = null;
		
		this.setup_page();
		this.setup_barcode_listener();
		this.load_dashboard();
	}

	setup_page() {
		// Add action buttons
		this.page.set_primary_action(__('Quick Stock In'), () => {
			this.show_quick_entry_dialog('Material Receipt');
		}, 'octicon octicon-plus');

		this.page.add_action_icon('octicon octicon-sign-out', () => {
			this.show_quick_entry_dialog('Material Issue');
		}, __('Quick Stock Out'));

		this.page.add_action_icon('octicon octicon-sync', () => {
			this.show_quick_entry_dialog('Material Transfer');
		}, __('Quick Transfer'));

		this.page.add_action_icon('refresh', () => {
			this.load_dashboard();
		}, __('Refresh'));

		// Create main layout
		this.parent.html(`
			<div class="stock-dashboard">
				<!-- Statistics Cards -->
				<div class="stats-section" style="margin-bottom: 20px;">
					<div class="row">
						<div class="col-md-3">
							<div class="stat-card" style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
								<div style="display: flex; justify-content: space-between; align-items: center;">
									<div>
										<h2 id="total-items" style="margin: 0; font-size: 36px;">0</h2>
										<p style="margin: 5px 0 0 0; opacity: 0.9;">${__('Total Items')}</p>
									</div>
									<i class="fa fa-cubes" style="font-size: 48px; opacity: 0.3;"></i>
								</div>
							</div>
						</div>
						<div class="col-md-3">
							<div class="stat-card" style="padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
								<div style="display: flex; justify-content: space-between; align-items: center;">
									<div>
										<h2 id="low-stock" style="margin: 0; font-size: 36px;">0</h2>
										<p style="margin: 5px 0 0 0; opacity: 0.9;">${__('Low Stock')}</p>
									</div>
									<i class="fa fa-exclamation-triangle" style="font-size: 48px; opacity: 0.3;"></i>
								</div>
							</div>
						</div>
						<div class="col-md-3">
							<div class="stat-card" style="padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
								<div style="display: flex; justify-content: space-between; align-items: center;">
									<div>
										<h2 id="out-of-stock" style="margin: 0; font-size: 36px;">0</h2>
										<p style="margin: 5px 0 0 0; opacity: 0.9;">${__('Out of Stock')}</p>
									</div>
									<i class="fa fa-times-circle" style="font-size: 48px; opacity: 0.3;"></i>
								</div>
							</div>
						</div>
						<div class="col-md-3">
							<div class="stat-card" style="padding: 20px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 10px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
								<div style="display: flex; justify-content: space-between; align-items: center;">
									<div>
										<h2 id="total-value" style="margin: 0; font-size: 28px;">$0</h2>
										<p style="margin: 5px 0 0 0; opacity: 0.9;">${__('Stock Value')}</p>
									</div>
									<i class="fa fa-money" style="font-size: 48px; opacity: 0.3;"></i>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Barcode Scanner Section -->
				<div class="barcode-section" style="margin-bottom: 20px;">
					<div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
						<div class="row">
							<div class="col-md-8">
								<label style="font-weight: bold; margin-bottom: 10px; display: block;">
									<i class="fa fa-barcode"></i> ${__('Barcode Scanner')}
								</label>
								<div style="display: flex; gap: 10px;">
									<input type="text" id="barcode-input" class="form-control" 
										placeholder="${__('Scan barcode or enter item code...')}" 
										style="flex: 1; font-size: 16px;">
									<button class="btn btn-primary" id="search-barcode">
										<i class="fa fa-search"></i> ${__('Search')}
									</button>
								</div>
							</div>
							<div class="col-md-4" id="scanned-item-info" style="display: none;">
								<div style="padding: 10px; background: #e8f5e9; border-radius: 5px;">
									<strong id="scanned-item-name"></strong><br>
									<small id="scanned-item-code"></small>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Main Content Area -->
				<div class="row">
					<!-- Left Column: Low Stock & Out of Stock -->
					<div class="col-md-6">
						<div class="low-stock-panel" style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
							<h4 style="margin: 0 0 15px 0; color: #f57c00;">
								<i class="fa fa-exclamation-triangle"></i> ${__('Low Stock Items')}
							</h4>
							<div id="low-stock-list">
								<div class="text-center" style="padding: 20px;">
									<i class="fa fa-spinner fa-spin"></i> ${__('Loading...')}
								</div>
							</div>
						</div>

						<div class="out-of-stock-panel" style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
							<h4 style="margin: 0 0 15px 0; color: #d32f2f;">
								<i class="fa fa-times-circle"></i> ${__('Out of Stock Items')}
							</h4>
							<div id="out-of-stock-list">
								<div class="text-center" style="padding: 20px;">
									<i class="fa fa-spinner fa-spin"></i> ${__('Loading...')}
								</div>
							</div>
						</div>
					</div>

					<!-- Right Column: Recent Movements & Top Items -->
					<div class="col-md-6">
						<div class="recent-movements-panel" style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
							<h4 style="margin: 0 0 15px 0; color: #1976d2;">
								<i class="fa fa-exchange"></i> ${__('Recent Stock Movements')}
							</h4>
							<div id="recent-movements-list">
								<div class="text-center" style="padding: 20px;">
									<i class="fa fa-spinner fa-spin"></i> ${__('Loading...')}
								</div>
							</div>
						</div>

						<div class="top-items-panel" style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
							<h4 style="margin: 0 0 15px 0; color: #388e3c;">
								<i class="fa fa-star"></i> ${__('Top Items by Value')}
							</h4>
							<div id="top-items-list">
								<div class="text-center" style="padding: 20px;">
									<i class="fa fa-spinner fa-spin"></i> ${__('Loading...')}
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		`);

		this.setup_event_handlers();
	}

	setup_event_handlers() {
		// Barcode search
		this.parent.find('#search-barcode').on('click', () => {
			let barcode = this.parent.find('#barcode-input').val();
			if (barcode) {
				this.search_by_barcode(barcode);
			}
		});

		this.parent.find('#barcode-input').on('keypress', (e) => {
			if (e.which === 13) { // Enter key
				let barcode = $(e.target).val();
				if (barcode) {
					this.search_by_barcode(barcode);
				}
			}
		});
	}

	setup_barcode_listener() {
		// Listen for barcode scanner input (typically very fast typing)
		$(document).on('keypress', (e) => {
			// Only capture if not in an input field
			if ($(e.target).is('input, textarea')) {
				return;
			}

			clearTimeout(this.barcode_timeout);
			
			if (e.which === 13) { // Enter - end of barcode
				if (this.barcode_buffer.length > 3) {
					this.search_by_barcode(this.barcode_buffer);
					this.barcode_buffer = '';
				}
			} else {
				this.barcode_buffer += String.fromCharCode(e.which);
				
				// Reset buffer after 100ms of inactivity
				this.barcode_timeout = setTimeout(() => {
					this.barcode_buffer = '';
				}, 100);
			}
		});
	}

	load_dashboard() {
		frappe.call({
			method: 'smart_stock.api.get_stock_dashboard_data',
			callback: (r) => {
				if (r.message) {
					this.render_dashboard(r.message);
				}
			}
		});
	}

	render_dashboard(data) {
		// Update statistics
		const stats = data.statistics;
		this.parent.find('#total-items').text(stats.total_items);
		this.parent.find('#low-stock').text(stats.low_stock);
		this.parent.find('#out-of-stock').text(stats.out_of_stock);
		this.parent.find('#total-value').text(format_currency(stats.total_value));

		// Render low stock items
		this.render_low_stock_items(data.low_stock_items);

		// Render out of stock items
		this.render_out_of_stock_items(data.out_of_stock_items);

		// Render recent movements
		this.render_recent_movements(data.recent_movements);

		// Render top items
		this.render_top_items(data.top_items);
	}

	render_low_stock_items(items) {
		if (!items || items.length === 0) {
			this.parent.find('#low-stock-list').html(`
				<div class="text-center text-muted" style="padding: 20px;">
					<i class="fa fa-check-circle" style="font-size: 48px; color: #4caf50;"></i>
					<p style="margin-top: 10px;">${__('All items are well stocked!')}</p>
				</div>
			`);
			return;
		}

		let html = '<div style="max-height: 400px; overflow-y: auto;">';
		
		items.forEach(item => {
			let percentage = (item.actual_qty / item.threshold) * 100;
			let color = percentage < 50 ? '#d32f2f' : '#f57c00';
			
			html += `
				<div class="stock-item-card" style="padding: 12px; border-left: 4px solid ${color}; background: #fff3e0; margin-bottom: 10px; border-radius: 4px; cursor: pointer;" 
					data-item-code="${item.item_code}">
					<div style="display: flex; justify-content: space-between; align-items: start;">
						<div style="flex: 1;">
							<strong style="color: #333;">${item.item_name}</strong><br>
							<small style="color: #666;">${item.item_code} • ${item.warehouse}</small>
						</div>
						<div style="text-align: right;">
							<div style="font-size: 24px; font-weight: bold; color: ${color};">
								${item.actual_qty}
							</div>
							<small style="color: #666;">/ ${item.threshold} ${item.stock_uom}</small>
						</div>
					</div>
					<div style="margin-top: 8px;">
						<div style="height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden;">
							<div style="height: 100%; background: ${color}; width: ${Math.min(percentage, 100)}%;"></div>
						</div>
					</div>
				</div>
			`;
		});
		
		html += '</div>';
		
		this.parent.find('#low-stock-list').html(html);

		// Add click handlers
		this.parent.find('.stock-item-card').on('click', (e) => {
			let item_code = $(e.currentTarget).data('item-code');
			this.show_item_details(item_code);
		});
	}

	render_out_of_stock_items(items) {
		if (!items || items.length === 0) {
			this.parent.find('#out-of-stock-list').html(`
				<div class="text-center text-muted" style="padding: 20px;">
					<i class="fa fa-check-circle" style="font-size: 48px; color: #4caf50;"></i>
					<p style="margin-top: 10px;">${__('No items out of stock!')}</p>
				</div>
			`);
			return;
		}

		let html = '<div style="max-height: 400px; overflow-y: auto;">';
		
		items.forEach(item => {
			html += `
				<div class="stock-item-card" style="padding: 12px; border-left: 4px solid #d32f2f; background: #ffebee; margin-bottom: 10px; border-radius: 4px; cursor: pointer;" 
					data-item-code="${item.item_code}">
					<div style="display: flex; justify-content: space-between; align-items: center;">
						<div style="flex: 1;">
							<strong style="color: #333;">${item.item_name}</strong><br>
							<small style="color: #666;">${item.item_code} • ${item.warehouse}</small>
						</div>
						<div style="text-align: right;">
							<span class="label label-danger">${__('OUT OF STOCK')}</span>
						</div>
					</div>
				</div>
			`;
		});
		
		html += '</div>';
		
		this.parent.find('#out-of-stock-list').html(html);

		// Add click handlers
		this.parent.find('.stock-item-card').on('click', (e) => {
			let item_code = $(e.currentTarget).data('item-code');
			this.show_item_details(item_code);
		});
	}

	render_recent_movements(movements) {
		if (!movements || movements.length === 0) {
			this.parent.find('#recent-movements-list').html(`
				<div class="text-center text-muted" style="padding: 20px;">
					<p>${__('No recent movements')}</p>
				</div>
			`);
			return;
		}

		let html = '<div style="max-height: 400px; overflow-y: auto;">';
		
		movements.forEach(mov => {
			let icon = mov.stock_entry_type === 'Material Receipt' ? 'sign-in' : 
					   mov.stock_entry_type === 'Material Issue' ? 'sign-out' : 'exchange';
			let color = mov.stock_entry_type === 'Material Receipt' ? '#4caf50' : 
						mov.stock_entry_type === 'Material Issue' ? '#f44336' : '#2196f3';
			
			html += `
				<div style="padding: 10px; border-bottom: 1px solid #eee; cursor: pointer;" 
					onclick="frappe.set_route('Form', 'Stock Entry', '${mov.name}')">
					<div style="display: flex; justify-content: space-between; align-items: center;">
						<div>
							<i class="fa fa-${icon}" style="color: ${color}; margin-right: 8px;"></i>
							<strong>${mov.name}</strong>
							<span class="label label-default" style="margin-left: 8px;">${mov.stock_entry_type}</span>
						</div>
						<small class="text-muted">${frappe.datetime.str_to_user(mov.posting_date)}</small>
					</div>
					${mov.from_warehouse || mov.to_warehouse ? `
						<small class="text-muted" style="margin-left: 24px;">
							${mov.from_warehouse ? mov.from_warehouse : ''} 
							${mov.from_warehouse && mov.to_warehouse ? ' → ' : ''}
							${mov.to_warehouse ? mov.to_warehouse : ''}
						</small>
					` : ''}
				</div>
			`;
		});
		
		html += '</div>';
		
		this.parent.find('#recent-movements-list').html(html);
	}

	render_top_items(items) {
		if (!items || items.length === 0) {
			this.parent.find('#top-items-list').html(`
				<div class="text-center text-muted" style="padding: 20px;">
					<p>${__('No items found')}</p>
				</div>
			`);
			return;
		}

		let html = '<div style="max-height: 400px; overflow-y: auto;">';
		
		items.forEach((item, index) => {
			html += `
				<div style="padding: 10px; border-bottom: 1px solid #eee; cursor: pointer;" 
					data-item-code="${item.item_code}">
					<div style="display: flex; justify-content: space-between; align-items: center;">
						<div style="display: flex; align-items: center; gap: 10px;">
							<div style="background: #4caf50; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">
								${index + 1}
							</div>
							<div>
								<strong>${item.item_name}</strong><br>
								<small class="text-muted">${item.total_qty} ${item.stock_uom}</small>
							</div>
						</div>
						<div style="text-align: right;">
							<strong style="color: #4caf50;">${format_currency(item.total_value)}</strong>
						</div>
					</div>
				</div>
			`;
		});
		
		html += '</div>';
		
		this.parent.find('#top-items-list').html(html);
	}

	search_by_barcode(barcode) {
		frappe.call({
			method: 'smart_stock.api.search_item_by_barcode',
			args: { barcode: barcode },
			callback: (r) => {
				if (r.message) {
					this.show_item_details_dialog(r.message);
					// Clear input
					this.parent.find('#barcode-input').val('').focus();
				} else {
					frappe.show_alert({
						message: __('Item not found for barcode: {0}', [barcode]),
						indicator: 'orange'
					});
				}
			}
		});
	}

	show_item_details(item_code) {
		frappe.call({
			method: 'smart_stock.api.get_item_details',
			args: { item_code: item_code },
			callback: (r) => {
				if (r.message) {
					this.show_item_details_dialog(r.message);
				}
			}
		});
	}

	show_item_details_dialog(item) {
		let d = new frappe.ui.Dialog({
			title: item.item_name,
			fields: [
				{
					fieldtype: 'HTML',
					options: this.get_item_details_html(item)
				}
			],
			primary_action_label: __('Stock In'),
			primary_action: () => {
				d.hide();
				this.show_quick_entry_dialog('Material Receipt', item.item_code);
			},
			secondary_action_label: __('Stock Out'),
			secondary_action: () => {
				d.hide();
				this.show_quick_entry_dialog('Material Issue', item.item_code);
			}
		});

		d.show();
	}

	get_item_details_html(item) {
		let html = `
			<div class="item-details-container">
				<div style="display: flex; gap: 20px; margin-bottom: 20px;">
					${item.image ? `
						<div style="flex-shrink: 0;">
							<img src="${item.image}" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px; border: 1px solid #ddd;">
						</div>
					` : ''}
					<div style="flex: 1;">
						<h4 style="margin: 0 0 5px 0;">${item.item_name}</h4>
						<p style="margin: 0; color: #666;"><small>${item.item_code}</small></p>
						<p style="margin: 10px 0 0 0;"><span class="label label-info">${item.item_group}</span></p>
					</div>
				</div>

				<h5 style="margin: 20px 0 10px 0; padding-bottom: 5px; border-bottom: 2px solid #eee;">
					${__('Stock Balance')}
				</h5>
				<table class="table table-bordered" style="margin: 0;">
					<thead>
						<tr>
							<th>${__('Warehouse')}</th>
							<th style="text-align: right;">${__('Quantity')}</th>
							<th style="text-align: right;">${__('Value')}</th>
						</tr>
					</thead>
					<tbody>
		`;

		if (item.stock_balance && item.stock_balance.length > 0) {
			item.stock_balance.forEach(bal => {
				let qty_color = bal.actual_qty > 0 ? '#4caf50' : '#f44336';
				html += `
					<tr>
						<td>${bal.warehouse}</td>
						<td style="text-align: right; color: ${qty_color}; font-weight: bold;">
							${bal.actual_qty} ${item.stock_uom}
						</td>
						<td style="text-align: right;">
							${format_currency(bal.actual_qty * bal.valuation_rate)}
						</td>
					</tr>
				`;
			});

			html += `
				<tr style="background: #f5f5f5; font-weight: bold;">
					<td>${__('Total')}</td>
					<td style="text-align: right;">${item.total_qty} ${item.stock_uom}</td>
					<td style="text-align: right;">
						${format_currency(item.stock_balance.reduce((sum, b) => sum + (b.actual_qty * b.valuation_rate), 0))}
					</td>
				</tr>
			`;
		} else {
			html += `
				<tr>
					<td colspan="3" class="text-center text-muted">${__('No stock available')}</td>
				</tr>
			`;
		}

		html += `
					</tbody>
				</table>
			</div>
		`;

		return html;
	}

	show_quick_entry_dialog(entry_type, item_code=null) {
		let title = entry_type === 'Material Receipt' ? __('Quick Stock In') :
					entry_type === 'Material Issue' ? __('Quick Stock Out') :
					__('Quick Stock Transfer');

		let fields = [
			{
				fieldname: 'entry_type',
				fieldtype: 'Data',
				label: __('Entry Type'),
				default: entry_type,
				read_only: 1,
				hidden: 1
			}
		];

		// Add warehouse fields based on entry type
		if (entry_type === 'Material Issue' || entry_type === 'Material Transfer') {
			fields.push({
				fieldname: 'from_warehouse',
				fieldtype: 'Link',
				options: 'Warehouse',
				label: __('From Warehouse'),
				reqd: 1
			});
		}

		if (entry_type === 'Material Receipt' || entry_type === 'Material Transfer') {
			fields.push({
				fieldname: 'to_warehouse',
				fieldtype: 'Link',
				options: 'Warehouse',
				label: __('To Warehouse'),
				reqd: 1
			});
		}

		fields.push(
			{
				fieldname: 'items_section',
				fieldtype: 'Section Break',
				label: __('Items')
			},
			{
				fieldname: 'items',
				fieldtype: 'Table',
				label: __('Items'),
				cannot_add_rows: false,
				cannot_delete_rows: false,
				fields: [
					{
						fieldname: 'item_code',
						fieldtype: 'Link',
						options: 'Item',
						label: __('Item'),
						reqd: 1,
						in_list_view: 1,
						get_query: () => {
							return {
								filters: {
									is_stock_item: 1,
									disabled: 0
								}
							};
						}
					},
					{
						fieldname: 'qty',
						fieldtype: 'Float',
						label: __('Quantity'),
						reqd: 1,
						in_list_view: 1
					},
					{
						fieldname: 'uom',
						fieldtype: 'Link',
						options: 'UOM',
						label: __('UOM'),
						read_only: 1,
						in_list_view: 1
					}
				]
			},
			{
				fieldname: 'remarks',
				fieldtype: 'Small Text',
				label: __('Remarks')
			}
		);

		let d = new frappe.ui.Dialog({
			title: title,
			fields: fields,
			primary_action_label: __('Create Stock Entry'),
			primary_action: (values) => {
				if (!values.items || values.items.length === 0) {
					frappe.msgprint(__('Please add at least one item'));
					return;
				}

				frappe.call({
					method: 'smart_stock.api.create_quick_stock_entry',
					args: {
						entry_type: values.entry_type,
						items: values.items,
						from_warehouse: values.from_warehouse,
						to_warehouse: values.to_warehouse,
						remarks: values.remarks
					},
					freeze: true,
					freeze_message: __('Creating Stock Entry...'),
					callback: (r) => {
						if (r.message && r.message.success) {
							frappe.show_alert({
								message: r.message.message,
								indicator: 'green'
							});
							d.hide();
							this.load_dashboard();
							
							// Ask if user wants to view the stock entry
							frappe.confirm(
								__('Stock Entry created successfully. Do you want to view it?'),
								() => {
									frappe.set_route('Form', 'Stock Entry', r.message.stock_entry);
								}
							);
						}
					}
				});
			}
		});

		// If item_code provided, add it to the items table
		if (item_code) {
			d.fields_dict.items.df.data = [{
				item_code: item_code,
				qty: 1
			}];
			d.fields_dict.items.grid.refresh();
		}

		d.show();
	}
}
