import frappe
from frappe.utils import getdate, today, get_first_day, get_last_day, add_months

@frappe.whitelist()
def get_dashboard_data(date_range=None, project=None, department=None, employee=None):
    conditions = []
    values = {}
    
    # Handle Date Range
    current_date = getdate(today())
    if date_range == 'This Month':
        start_date = get_first_day(current_date)
        end_date = get_last_day(current_date)
    elif date_range == 'Last Month':
        last_month = add_months(current_date, -1)
        start_date = get_first_day(last_month)
        end_date = get_last_day(last_month)
    elif date_range == 'This Year':
        start_date = current_date.replace(month=1, day=1) # Jan 1st
        end_date = current_date.replace(month=12, day=31) # Dec 31st
    else:
        # Default to This Month
        start_date = get_first_day(current_date)
        end_date = get_last_day(current_date)
        
    conditions.append("ts.start_date >= %(start_date)s")
    conditions.append("ts.start_date <= %(end_date)s")
    values['start_date'] = start_date
    values['end_date'] = end_date

    if project:
        conditions.append("td.project = %(project)s")
        values['project'] = project
    if department:
        conditions.append("ts.department = %(department)s")
        values['department'] = department
    if employee:
        conditions.append("ts.employee = %(employee)s")
        values['employee'] = employee
        
    condition_str = " AND " + " AND ".join(conditions) if conditions else ""
        
    query = f"""
        SELECT 
            ts.employee_name as employee,
            ts.employee as employee_id,
            SUM(td.hours) as utilized_hours,
            SUM(IF(td.is_billable=1, td.hours, 0)) as billable_hours,
            SUM(IF(td.is_billable=0, td.hours, 0)) as non_billable_hours,
            COUNT(DISTINCT td.project) as project_count,
            COUNT(DISTINCT td.task) as task_count,
            SUM(td.expected_hours) as expected_hours
        FROM `tabTimesheet` ts
        JOIN `tabTimesheet Detail` td ON ts.name = td.parent
        WHERE ts.docstatus = 1 {condition_str}
        GROUP BY ts.employee_name
        ORDER BY utilized_hours DESC
        LIMIT 10
    """
    
    data = frappe.db.sql(query, values, as_dict=True)
    
    total_utilized_hours = 0
    avg_utilization = 0
    
    if data:
        total_utilized_hours = sum([d.utilized_hours for d in data])
        
        # Calculate Average Utilization based on expected vs utilized for the resources returned
        # If expected_hours is 0 or very small (causing 54000% bugs), we fallback to standard 160 hrs per employee
        total_expected = sum([d.expected_hours or 0 for d in data])
        if total_expected < total_utilized_hours: 
            # If expected is suspiciously low or missing, assume standard 160 hrs/month * employee count
            total_expected = len(data) * 160
            
        if total_expected > 0:
            avg_utilization = int((total_utilized_hours / total_expected) * 100)
        else:
            avg_utilization = 0
            
        # Clamp between 0 and 100 for gauge
        avg_utilization = max(0, min(100, avg_utilization))
            
        for d in data:
            # Projects
            d.projects = frappe.db.sql_list(
                "SELECT DISTINCT project FROM `tabTimesheet Detail` WHERE parent IN (SELECT name FROM `tabTimesheet` WHERE employee_name=%s AND docstatus=1) AND project IS NOT NULL", 
                (d.employee,)
            )
            d.assigned_tasks = d.task_count
            
            # Completed tasks
            completed_tasks_query = "SELECT DISTINCT task FROM `tabTimesheet Detail` WHERE parent IN (SELECT name FROM `tabTimesheet` WHERE employee_name=%s)"
            tasks = frappe.db.sql(completed_tasks_query, (d.employee,))
            task_names = [t[0] for t in tasks if t[0]]
            
            if task_names:
                d.completed_tasks = frappe.db.count("Task", {"status": "Completed", "name": ("in", task_names)})
            else:
                d.completed_tasks = 0
                
            # Availability %
            emp_expected = d.expected_hours or 160
            if emp_expected < d.utilized_hours:
                emp_expected = max(160, d.utilized_hours) # Avoid negative availability if they worked overtime
                
            avail = ((emp_expected - d.utilized_hours) / emp_expected) * 100
            d.availability = max(0, min(100, int(avail)))

    return {
        "total_utilized_hours": f"{total_utilized_hours:,.2f}",
        "avg_utilization": avg_utilization,
        "chart_labels": [d.get("employee") for d in data],
        "chart_billable": [d.get("billable_hours") for d in data],
        "chart_non_billable": [d.get("non_billable_hours") for d in data],
        "table_data": data
    }
