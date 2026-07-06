frappe.pages['smarthr-admin-dashbo'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Admin Dashboard',
		single_column: true
	});
	
	$(wrapper).find('.page-head').hide();
	$(wrapper).find('.layout-main-section').css('background-color', '#f8f9fa');

	// Load Data First
	frappe.call({
		method: 'custom_biz.api.dashboard_api.get_dashboard_data',
		callback: function(r) {
			if (r.message) {
				render_dashboard(wrapper, r.message);
			}
		}
	});
}

function render_dashboard(wrapper, data) {
	// Formatters
	const formatCurrency = (val) => '₹' + (val || 0).toLocaleString('en-IN', {minimumFractionDigits: 0, maximumFractionDigits: 0});
	
	// Dynamic Department Bars
	let deptHTML = '';
	if (data.departments && data.departments.length > 0) {
		let maxCount = Math.max(...data.departments.map(d => d.count)) || 1;
		data.departments.slice(0, 6).forEach(dept => {
			let width = (dept.count / maxCount) * 100;
			deptHTML += `
				<div class="css-bar-row">
					<div class="css-bar-label">${dept.department}</div>
					<div class="css-bar-track"><div class="css-bar-fill" style="width: ${width}%;"></div></div>
				</div>
			`;
		});
	} else {
		deptHTML = `<p style="color:#6b7280; font-size:12px;">No department data</p>`;
	}
	
	// Dynamic Employee Status Stacked Bar
	let empTypeHTML = '';
	let empTypeLabels = '';
	const colors = ['#f59e0b', '#0f766e', '#ec4899', '#3b82f6'];
	if (data.employment_types && data.employment_types.length > 0) {
		let totalEmp = data.attendance.total || 1;
		data.employment_types.slice(0, 4).forEach((type, idx) => {
			let width = (type.count / totalEmp) * 100;
			let color = colors[idx % colors.length];
			empTypeHTML += `<div class="stack-part" style="width: ${width}%; background: ${color};"></div>`;
			empTypeLabels += `
				<div class="stack-label">
					<div class="stack-dot" style="background: ${color};"></div> 
					${type.employment_type} (${Math.round(width)}%)
				</div>
			`;
		});
	} else {
		empTypeHTML = `<div class="stack-part" style="width: 100%; background: #e5e7eb;"></div>`;
		empTypeLabels = `<div class="stack-label">No employment type data</div>`;
	}
	
	// Dynamic Clockins
	let clockinsHTML = '';
	if (data.checkins && data.checkins.length > 0) {
		data.checkins.forEach(c => {
			let avatar = c.image || `https://ui-avatars.com/api/?name=${encodeURIComponent(c.employee_name)}&background=e5e7eb`;
			let time = c.time ? frappe.datetime.get_time(c.time) : '';
			let icon = c.log_type === 'IN' ? 'fa-sign-in' : 'fa-sign-out';
			clockinsHTML += `
				<div class="clock-item">
					<div class="clock-user">
						<div class="clock-avatar"><img src="${avatar}" alt="${c.employee_name}"></div>
						<div class="clock-info">
							<h4>${c.employee_name}</h4>
							<p>${c.designation || 'Employee'}</p>
						</div>
					</div>
					<div class="clock-time"><i class="fa ${icon}"></i> ${time}</div>
				</div>
			`;
		});
	} else {
		clockinsHTML = `<p style="color:#6b7280; font-size:12px;">No recent check-ins</p>`;
	}

	const content = `
		<style>
			.smarthr-dashboard { font-family: 'Inter', 'Roboto', sans-serif; background-color: #f8f9fa; padding: 20px; color: #333; }
			.smarthr-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
			.smarthr-title h1 { font-size: 24px; font-weight: 700; margin: 0 0 5px 0; color: #1f2937; }
			.smarthr-breadcrumbs { font-size: 13px; color: #6b7280; }
			.smarthr-breadcrumbs span { color: #1f2937; font-weight: 500; }
			.smarthr-header-actions { display: flex; gap: 12px; }
			.smarthr-btn { display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; border: 1px solid #e5e7eb; background: #fff; color: #374151; transition: all 0.2s; }
			.smarthr-btn:hover { background: #f3f4f6; }
			
			.smarthr-welcome { background: #fff; border-radius: 10px; padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
			.smarthr-welcome-left { display: flex; align-items: center; gap: 16px; }
			.smarthr-avatar { width: 50px; height: 50px; border-radius: 50%; background: #f59e0b; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; font-weight: bold; overflow: hidden; }
			.smarthr-avatar img { width: 100%; height: 100%; object-fit: cover; }
			.smarthr-welcome-text h2 { font-size: 20px; font-weight: 700; margin: 0 0 4px 0; color: #111827; }
			.smarthr-welcome-text p { margin: 0; font-size: 14px; color: #6b7280; }
			.smarthr-welcome-text p span.text-orange { color: #f97316; font-weight: 500; }
			.smarthr-welcome-actions { display: flex; gap: 12px; }
			.btn-schedule { background: #064e3b; color: white; border: none; }
			.btn-schedule:hover { background: #042f2e; }
			.btn-requests { background: #f97316; color: white; border: none; }
			.btn-requests:hover { background: #ea580c; }
			
			.smarthr-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
			.smarthr-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
			
			.smarthr-kpi-card { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; flex-direction: column; gap: 12px; position: relative; }
			.kpi-icon { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
			.kpi-title { font-size: 13px; color: #6b7280; font-weight: 500; }
			.kpi-value-row { display: flex; align-items: baseline; gap: 8px; }
			.kpi-value { font-size: 22px; font-weight: 700; color: #1f2937; }
			.kpi-trend { font-size: 12px; font-weight: 600; }
			.trend-up { color: #10b981; }
			.trend-down { color: #ef4444; }
			.kpi-link { font-size: 13px; color: #6b7280; text-decoration: none; margin-top: auto; }
			.kpi-link:hover { color: #111827; }
			
			.chart-card { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
			.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
			.chart-title { font-size: 16px; font-weight: 600; color: #1f2937; margin: 0; }
			.chart-dropdown { padding: 4px 8px; border: 1px solid #e5e7eb; border-radius: 4px; font-size: 12px; color: #4b5563; background: white; }
			
			.css-bar-chart { display: flex; flex-direction: column; gap: 16px; }
			.css-bar-row { display: flex; align-items: center; gap: 12px; }
			.css-bar-label { width: 90px; font-size: 13px; color: #4b5563; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
			.css-bar-track { flex: 1; height: 12px; background: #f3f4f6; border-radius: 6px; overflow: hidden; }
			.css-bar-fill { height: 100%; background: #f97316; border-radius: 6px; }
			
			.stacked-total { font-size: 24px; font-weight: 700; text-align: right; margin-bottom: 12px; }
			.stacked-track { height: 16px; border-radius: 8px; display: flex; overflow: hidden; margin-bottom: 20px; }
			.stack-part { height: 100%; }
			.stack-labels { display: flex; flex-wrap: wrap; gap: 12px; justify-content: space-between; font-size: 12px; color: #6b7280; }
			.stack-label { display: flex; align-items: center; gap: 6px; }
			.stack-dot { width: 8px; height: 8px; border-radius: 50%; }

			.clock-list { display: flex; flex-direction: column; gap: 16px; }
			.clock-item { display: flex; justify-content: space-between; align-items: center; }
			.clock-user { display: flex; align-items: center; gap: 12px; }
			.clock-avatar { width: 36px; height: 36px; border-radius: 50%; background: #e5e7eb; overflow: hidden; }
			.clock-avatar img { width: 100%; height: 100%; object-fit: cover; }
			.clock-info h4 { margin: 0; font-size: 14px; font-weight: 600; color: #1f2937; }
			.clock-info p { margin: 0; font-size: 12px; color: #6b7280; }
			.clock-time { background: #dcfce7; color: #16a34a; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 4px; }
			
			.donut-chart-container { display: flex; justify-content: center; align-items: center; height: 200px; position: relative; }
			.donut-mock {
				width: 180px; height: 180px; border-radius: 50%;
				/* Simple conic gradient based on attendance */
				background: conic-gradient(
					#047857 0deg ${((data.attendance.present / (data.attendance.total || 1)) * 360)}deg,
					#e5e7eb ${((data.attendance.present / (data.attendance.total || 1)) * 360)}deg 360deg
				);
				position: relative; display: flex; align-items: center; justify-content: center;
			}
			.donut-mock::after { content: ''; width: 120px; height: 120px; background: #fff; border-radius: 50%; position: absolute; }

			@media (max-width: 1200px) { .smarthr-grid { grid-template-columns: repeat(2, 1fr); } .smarthr-grid-3 { grid-template-columns: repeat(2, 1fr); } }
			@media (max-width: 768px) { .smarthr-grid { grid-template-columns: 1fr; } .smarthr-grid-3 { grid-template-columns: 1fr; } .smarthr-welcome { flex-direction: column; align-items: flex-start; gap: 16px; } }
		</style>
		
		<div class="smarthr-dashboard">
			<div class="smarthr-header">
				<div class="smarthr-title">
					<h1>Admin Dashboard</h1>
					<div class="smarthr-breadcrumbs"><i class="fa fa-home"></i> / Dashboard / <span>Admin Dashboard</span></div>
				</div>
				<div class="smarthr-header-actions">
					<button class="smarthr-btn"><i class="fa fa-download"></i> Export</button>
				</div>
			</div>
			
			<div class="smarthr-welcome">
				<div class="smarthr-welcome-left">
					<div class="smarthr-avatar">
						<img src="https://ui-avatars.com/api/?name=${encodeURIComponent(data.user_fullname)}&background=f59e0b&color=fff">
					</div>
					<div class="smarthr-welcome-text">
						<h2>Welcome Back, ${data.user_fullname} <i class="fa fa-pencil" style="font-size:12px; color:#9ca3af; cursor:pointer;"></i></h2>
						<p>You have <span class="text-orange">${data.pending_approvals}</span> Pending Approvals & <span class="text-orange">${data.leave_requests}</span> Leave Requests</p>
					</div>
				</div>
				<div class="smarthr-welcome-actions">
					<button class="smarthr-btn btn-schedule"><i class="fa fa-calendar-plus-o"></i> Add Schedule</button>
					<button class="smarthr-btn btn-requests"><i class="fa fa-plus-circle"></i> Add Requests</button>
				</div>
			</div>
			
			<div class="smarthr-grid">
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #ffede6; color: #ea580c;"><i class="fa fa-calendar-check-o"></i></div>
					<div class="kpi-title">Attendance Overview</div>
					<div class="kpi-value-row">
						<span class="kpi-value">${data.attendance.present}/${data.attendance.total}</span>
					</div>
					<a href="/app/attendance" class="kpi-link" style="color: #ea580c;">View Details</a>
				</div>
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #e6eff1; color: #0f766e;"><i class="fa fa-folder-o"></i></div>
					<div class="kpi-title">Total No of Projects</div>
					<div class="kpi-value-row"><span class="kpi-value">${data.projects}</span></div>
					<a href="/app/project" class="kpi-link">View All</a>
				</div>
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #eff6ff; color: #3b82f6;"><i class="fa fa-users"></i></div>
					<div class="kpi-title">Total No of Clients</div>
					<div class="kpi-value-row"><span class="kpi-value">${data.clients}</span></div>
					<a href="/app/customer" class="kpi-link">View All</a>
				</div>
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #fce7f3; color: #ec4899;"><i class="fa fa-tasks"></i></div>
					<div class="kpi-title">Total No of Tasks</div>
					<div class="kpi-value-row"><span class="kpi-value">${data.tasks}</span></div>
					<a href="/app/task" class="kpi-link">View All</a>
				</div>
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #f3e8ff; color: #a855f7;"><i class="fa fa-money"></i></div>
					<div class="kpi-title">Earnings this Week</div>
					<div class="kpi-value-row"><span class="kpi-value">${formatCurrency(data.earnings)}</span></div>
					<a href="/app/sales-invoice" class="kpi-link">View Transactions</a>
				</div>
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #fee2e2; color: #ef4444;"><i class="fa fa-line-chart"></i></div>
					<div class="kpi-title">Profit This Week</div>
					<div class="kpi-value-row"><span class="kpi-value">${formatCurrency(data.profit)}</span></div>
					<a href="/app/query-report/General%20Ledger" class="kpi-link">View Earnings</a>
				</div>
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #dcfce7; color: #22c55e;"><i class="fa fa-user-plus"></i></div>
					<div class="kpi-title">Job Applicants</div>
					<div class="kpi-value-row"><span class="kpi-value">${data.job_applicants}</span></div>
					<a href="/app/job-applicant" class="kpi-link">View All</a>
				</div>
				<div class="smarthr-kpi-card">
					<div class="kpi-icon" style="background: #f3f4f6; color: #1f2937;"><i class="fa fa-user-circle"></i></div>
					<div class="kpi-title">New Hire This month</div>
					<div class="kpi-value-row"><span class="kpi-value">${data.new_hires}</span></div>
					<a href="/app/employee" class="kpi-link">View Candidates</a>
				</div>
			</div>
			
			<div class="smarthr-grid-3">
				<!-- Employees By Department -->
				<div class="chart-card">
					<div class="chart-header">
						<h3 class="chart-title">Employees By Department</h3>
					</div>
					<div class="css-bar-chart">
						${deptHTML}
					</div>
				</div>
				
				<!-- Employee Status -->
				<div class="chart-card">
					<div class="chart-header">
						<h3 class="chart-title">Employee Status</h3>
					</div>
					<p style="color: #6b7280; font-size: 13px; margin: 0 0 5px 0;">Total Employee</p>
					<div class="stacked-total">${data.attendance.total}</div>
					
					<div class="stacked-track">
						${empTypeHTML}
					</div>
					
					<div class="stack-labels">
						${empTypeLabels}
					</div>
				</div>
				
				<div style="display: flex; flex-direction: column; gap: 20px;">
					<!-- Attendance Doughnut -->
					<div class="chart-card">
						<div class="chart-header">
							<h3 class="chart-title">Attendance Overview</h3>
						</div>
						<div class="donut-chart-container">
							<div class="donut-mock"></div>
							<div style="position: absolute; text-align: center;">
								<div style="font-size: 24px; font-weight: 700; color: #1f2937;">${data.attendance.present}</div>
								<div style="font-size: 12px; color: #6b7280;">Present</div>
							</div>
						</div>
					</div>
					
					<!-- Clock In/Out -->
					<div class="chart-card">
						<div class="chart-header" style="margin-bottom: 16px;">
							<h3 class="chart-title">Recent Check-Ins</h3>
						</div>
						<div class="clock-list">
							${clockinsHTML}
						</div>
					</div>
				</div>
			</div>
		</div>
	`;
	
	$(wrapper).find('.layout-main-section').html(content);

	// Bind interactive buttons to standard ERPNext HRMS DocTypes
	$(wrapper).find('.btn-schedule').on('click', function() {
		frappe.prompt([
			{
				label: 'Schedule Type',
				fieldname: 'doctype',
				fieldtype: 'Select',
				options: 'Event\nInterview\nShift Assignment',
				reqd: 1
			}
		], (values) => {
			frappe.new_doc(values.doctype);
		}, 'Add Schedule', 'Create');
	});
	
	$(wrapper).find('.btn-requests').on('click', function() {
		frappe.prompt([
			{
				label: 'Request Type',
				fieldname: 'doctype',
				fieldtype: 'Select',
				options: 'Leave Application\nJob Requisition\nAttendance Request\nExpense Claim',
				reqd: 1
			}
		], (values) => {
			frappe.new_doc(values.doctype);
		}, 'Add Request', 'Create');
	});
}