frappe.pages['resource-workload-da'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Resource Workload Dashboard',
		single_column: true
	});

    page.add_field({
        fieldname: 'date_range',
        label: __('Date Range'),
        fieldtype: 'Select',
        options: ['This Month', 'Last Month', 'This Year'],
        default: 'This Month',
        change: function() {
            refresh_dashboard(page);
        }
    });

    page.add_field({
        fieldname: 'project',
        label: __('Project'),
        fieldtype: 'Link',
        options: 'Project',
        change: function() {
            refresh_dashboard(page);
        }
    });

    page.add_field({
        fieldname: 'employee',
        label: __('Employee'),
        fieldtype: 'Link',
        options: 'Employee',
        change: function() {
            refresh_dashboard(page);
        }
    });

    page.add_field({
        fieldname: 'department',
        label: __('Department'),
        fieldtype: 'Link',
        options: 'Department',
        change: function() {
            refresh_dashboard(page);
        }
    });

    page.add_inner_button(__('Actions'), function() {
        // Dummy action button
    });
    
    // UI Tweaks to match the header mockup exactly
    setTimeout(() => {
        let dr_wrap = page.fields_dict.date_range.$wrapper;
        let dr_label = dr_wrap.find('.control-label');
        dr_label.html('Date Range').css({
            'font-size': '11px',
            'font-weight': 'normal',
            'color': '#4b5563',
            'margin-bottom': '4px',
            'text-align': 'left'
        });
        dr_label[0].style.setProperty('display', 'block', 'important');
        dr_wrap.find('.control-input').css('width', '130px');
        
        let prj_wrap = page.fields_dict.project.$wrapper;
        let prj_label = prj_wrap.find('.control-label');
        prj_label.html('&nbsp;').css({
            'font-size': '11px',
            'margin-bottom': '4px'
        });
        prj_label[0].style.setProperty('display', 'block', 'important');
        prj_wrap.find('input').attr('placeholder', 'Project').css('width', '130px');
        
        let dept_wrap = page.fields_dict.department.$wrapper;
        let dept_label = dept_wrap.find('.control-label');
        dept_label.html('&nbsp;').css({
            'font-size': '11px',
            'margin-bottom': '4px'
        });
        dept_label[0].style.setProperty('display', 'block', 'important');
        dept_wrap.find('input').attr('placeholder', 'Department').css('width', '130px');

        let emp_wrap = page.fields_dict.employee.$wrapper;
        let emp_label = emp_wrap.find('.control-label');
        emp_label.html('&nbsp;').css({
            'font-size': '11px',
            'margin-bottom': '4px'
        });
        emp_label[0].style.setProperty('display', 'block', 'important');
        emp_wrap.find('input').attr('placeholder', 'Employee').css('width', '130px');

        // Move the entire page-form (filters) to the right side, inline with the Actions button
        let page_form = page.wrapper.find('.page-form');
        let page_actions = page.wrapper.find('.page-actions');
        
        page_form.prependTo(page_actions);
        page_form.css({
            'display': 'flex',
            'align-items': 'flex-end',
            'margin-bottom': '0px',
            'margin-right': '10px',
            'padding': '0px',
            'border': 'none'
        });
        
        page_actions.css({
            'display': 'flex',
            'align-items': 'flex-end',
            'justify-content': 'flex-end'
        });
        
        // Remove margin from the form wrappers to make them perfectly inline
        page_form.find('.frappe-control').css({
            'margin-bottom': '0px',
            'margin-right': '10px'
        });
        
    }, 100);

	// Inject HTML
	$(frappe.render_template("resource_workload_da", {})).appendTo(page.main);

    // Initial Render
    refresh_dashboard(page);
}

function refresh_dashboard(page) {
    let filters = {
        date_range: page.fields_dict.date_range.get_value(),
        project: page.fields_dict.project.get_value(),
        department: page.fields_dict.department.get_value(),
        employee: page.fields_dict.employee.get_value(),
    };

    frappe.call({
        method: "custom_biz.api.resource_dashboard.get_dashboard_data",
        args: filters,
        callback: function(r) {
            if(r.message) {
                render_dashboard(r.message, page);
            }
        }
    });
}

function render_dashboard(data, page) {
    // 1. KPI Cards
    page.main.find('#kpi-total-hours').text(data.total_utilized_hours);
    page.main.find('#kpi-avg-util').text(data.avg_utilization + ' %');

    // 2. Gauge Chart
    let gauge_val = data.avg_utilization;
    if (gauge_val > 100) gauge_val = 100;
    if (gauge_val < 0) gauge_val = 0;
    
    // Needle rotation (0 to 180 degrees)
    let needle_rot = (gauge_val / 100) * 180;
    
    let svg_html = `
    <svg viewBox="0 0 100 55" style="width: 100%; height: 100%; overflow: visible;">
        <!-- Red 0-33% (180deg to 120deg) -->
        <path d="M 10 50 A 40 40 0 0 1 30 15.36" fill="none" stroke="#cb4b46" stroke-width="14" />
        <!-- Yellow 33-66% (120deg to 60deg) -->
        <path d="M 30 15.36 A 40 40 0 0 1 70 15.36" fill="none" stroke="#eeb756" stroke-width="14" />
        <!-- Grey 66-100% (60deg to 0deg) -->
        <path d="M 70 15.36 A 40 40 0 0 1 90 50" fill="none" stroke="#dbe0e6" stroke-width="14" />
        
        <!-- Needle pointing left initially, then rotated -->
        <g transform="rotate(${needle_rot}, 50, 50)">
            <polygon points="50,48 50,52 14,50" fill="#3b4856" />
            <circle cx="50" cy="50" r="3.5" fill="#3b4856" />
        </g>
    </svg>
    `;
    
    // Add the red dot next to the value
    page.main.find('#kpi-avg-util').html(data.avg_utilization + ' % <span style="color: #ff4d4f; font-size: 28px; line-height: 0; vertical-align: middle; margin-left: 5px;">.</span>');
    page.main.find("#gauge-chart").html(svg_html);

    // 3. Bar Chart (Top 10 Utilized Resources)
    let max_hours = 0;
    for (let i = 0; i < data.chart_labels.length; i++) {
        let total = (data.chart_billable[i] || 0) + (data.chart_non_billable[i] || 0);
        if (total > max_hours) max_hours = total;
    }
    
    // Determine scale max (e.g. 240)
    let scale_max = Math.ceil(max_hours / 40) * 40 || 240;
    if (scale_max < 240) scale_max = 240;
    
    let chart_html = '<div class="custom-hz-chart">';
    
    // Grid Lines overlay
    chart_html += '<div style="position: absolute; left: 120px; top: 0; bottom: 80px; right: 0; pointer-events: none;">';
    for (let i = 40; i <= scale_max; i += 40) {
        let p_tick = (i / scale_max) * 100;
        chart_html += `<div style="position: absolute; left: ${p_tick}%; top: 0; bottom: 0; border-left: 1px solid #e5e7eb; z-index: 0;"></div>`;
    }
    chart_html += '</div>';
    
    // Rows
    for (let i = 0; i < data.chart_labels.length; i++) {
        let billable = data.chart_billable[i] || 0;
        let non_billable = data.chart_non_billable[i] || 0;
        
        let p_billable = (billable / scale_max) * 100;
        let p_non_billable = (non_billable / scale_max) * 100;
        
        chart_html += `
            <div class="hz-row">
                <div class="hz-label" title="${data.chart_labels[i]}">${data.chart_labels[i]}</div>
                <div class="hz-bar-container">
                    <div class="hz-bar-billable" style="width: ${p_billable}%; z-index: 1;" title="Billable: ${billable}"></div>
                    <div class="hz-bar-nonbillable" style="width: ${p_non_billable}%; z-index: 1;" title="Non-Billable: ${non_billable}"></div>
                </div>
            </div>
        `;
    }
    
    // X Axis Ticks
    chart_html += '<div class="hz-x-axis">';
    for (let i = 0; i <= scale_max; i += 40) {
        let p_tick = (i / scale_max) * 100;
        chart_html += `<div class="hz-x-tick" style="left: ${p_tick}%;">${i}</div>`;
    }
    chart_html += '</div>';
    
    // X Axis Title
    chart_html += '<div class="hz-x-title">Hours Logged</div>';
    
    // Legend
    chart_html += `
        <div class="hz-legend">
            <div class="hz-legend-item">
                <div class="hz-legend-color hz-bar-billable"></div> Billable Hours
            </div>
            <div class="hz-legend-item">
                <div class="hz-legend-color hz-bar-nonbillable"></div> Non-Billable Hours
            </div>
        </div>
    `;
    chart_html += '</div>';
    
    page.main.find("#bar-chart").html(chart_html);

    // 4. Data Table
    let tbody = page.main.find("#resource-table-body");
    tbody.empty();

    data.table_data.forEach(row => {
        let projects_html = "";
        row.projects.forEach(p => {
            projects_html += `<span class="badge-project">${p}</span>`;
        });

        // Determine badge color based on availability
        let avail_bg = "#d1fae5";
        let avail_color = "#065f46";
        if (row.availability < 70) {
            avail_bg = "#fee2e2";
            avail_color = "#991b1b";
        } else if (row.availability < 85) {
            avail_bg = "#fef3c7";
            avail_color = "#92400e";
        }

        let tr = `
            <tr>
                <td><input type="checkbox" disabled class="text-muted"></td>
                <td>${row.employee}</td>
                <td>${projects_html}</td>
                <td class="text-center">${row.assigned_tasks}</td>
                <td class="text-center">${row.completed_tasks}</td>
                <td class="text-center">${row.utilized_hours}</td>
                <td class="text-center"><span class="badge-availability" style="background-color: ${avail_bg}; color: ${avail_color}">${row.availability}%</span></td>
            </tr>
        `;
        tbody.append(tr);
    });
}