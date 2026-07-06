import frappe
from frappe.utils import today, getdate, add_days, get_first_day, get_last_day

@frappe.whitelist()
def get_dashboard_data():
    current_date = today()
    current_user = frappe.session.user
    
    # 1. User Name
    user_fullname = frappe.db.get_value("User", current_user, "full_name") or current_user
    
    # 2. Leave Requests & Pending Approvals
    # Assuming pending approvals = submitted Leave Applications with status = Open
    pending_leaves = frappe.db.count("Leave Application", {"status": "Open", "docstatus": 1})
    
    # 3. Attendance Overview
    total_employees = frappe.db.count("Employee", {"status": "Active"})
    present_today = frappe.db.count("Attendance", {"attendance_date": current_date, "status": "Present", "docstatus": 1})
    
    # 4. Total Projects, Clients, Tasks
    total_projects = frappe.db.count("Project", {"status": "Open"}) if frappe.db.exists("DocType", "Project") else 0
    total_clients = frappe.db.count("Customer", {"disabled": 0}) if frappe.db.exists("DocType", "Customer") else 0
    total_tasks = frappe.db.count("Task", {"status": ["in", ["Open", "Working"]]}) if frappe.db.exists("DocType", "Task") else 0

    # 5. Financials (This Week)
    earnings_this_week = 0
    profit_this_week = 0
    
    # Calculate dates for "This Week"
    current_date_obj = getdate(current_date)
    week_start = add_days(current_date, - current_date_obj.weekday()) # Monday
    week_end = add_days(week_start, 6) # Sunday
    
    if frappe.db.exists("DocType", "GL Entry"):
        # Real Earnings from General Ledger (Income accounts)
        income_data = frappe.db.sql("""
            SELECT SUM(credit - debit) as income
            FROM `tabGL Entry`
            WHERE posting_date BETWEEN %s AND %s
            AND account IN (SELECT name FROM `tabAccount` WHERE root_type = 'Income')
            AND is_cancelled = 0
        """, (week_start, week_end), as_dict=True)
        
        # Real Expenses from General Ledger (Expense accounts)
        expense_data = frappe.db.sql("""
            SELECT SUM(debit - credit) as expense
            FROM `tabGL Entry`
            WHERE posting_date BETWEEN %s AND %s
            AND account IN (SELECT name FROM `tabAccount` WHERE root_type = 'Expense')
            AND is_cancelled = 0
        """, (week_start, week_end), as_dict=True)
        
        earnings_this_week = income_data[0].income if income_data and income_data[0].income else 0
        expenses = expense_data[0].expense if expense_data and expense_data[0].expense else 0
        profit_this_week = earnings_this_week - expenses
        
    # 6. HR metrics
    job_applicants = frappe.db.count("Job Applicant", {"status": "Open"}) if frappe.db.exists("DocType", "Job Applicant") else 0
    
    # New hires this month
    first_day = get_first_day(current_date)
    last_day = get_last_day(current_date)
    new_hires = frappe.db.count("Employee", {"date_of_joining": ["between", [first_day, last_day]]})
    
    # 7. Employees by Department
    department_counts = frappe.db.sql("""
        SELECT department, COUNT(name) as count 
        FROM `tabEmployee` 
        WHERE status='Active' AND department IS NOT NULL 
        GROUP BY department
    """, as_dict=True)
    
    # 8. Employee Status (Employment Type)
    employment_types = frappe.db.sql("""
        SELECT employment_type, COUNT(name) as count 
        FROM `tabEmployee` 
        WHERE status='Active' AND employment_type IS NOT NULL 
        GROUP BY employment_type
    """, as_dict=True)
    
    # 9. Clock-In/Out
    # Recent Check-ins
    checkins = []
    if frappe.db.exists("DocType", "Employee Checkin"):
        checkins = frappe.db.sql("""
            SELECT c.employee_name, c.time, c.log_type, e.designation, e.image 
            FROM `tabEmployee Checkin` c
            LEFT JOIN `tabEmployee` e ON c.employee = e.name
            ORDER BY c.time DESC LIMIT 5
        """, as_dict=True)
    
    return {
        "user_fullname": user_fullname,
        "pending_approvals": pending_leaves,
        "leave_requests": pending_leaves,
        "attendance": {
            "present": present_today,
            "total": total_employees
        },
        "projects": total_projects,
        "clients": total_clients,
        "tasks": total_tasks,
        "earnings": earnings_this_week,
        "profit": profit_this_week,
        "job_applicants": job_applicants,
        "new_hires": new_hires,
        "departments": department_counts,
        "employment_types": employment_types,
        "checkins": checkins
    }
