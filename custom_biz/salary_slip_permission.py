import frappe

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
        
    if user == "Administrator":
        return ""
        
    roles = frappe.get_roles(user)
    # Roles that can see all salary slips
    admin_roles = ["HR Manager", "HR User", "Payroll Manager", "Payroll Administrator", "System Manager"]
    if any(role in roles for role in admin_roles):
        return ""
        
    # Get active employee linked to the user
    employee = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"})
    
    if not employee:
        # If user is not an employee and has no admin roles, they shouldn't see any
        return "1=0"
        
    # Get all juniors
    juniors = get_all_juniors(employee)
    
    allowed_employees = [employee] + juniors
    
    employees_str = ", ".join([frappe.db.escape(e) for e in allowed_employees])
    return f"`tabSalary Slip`.employee in ({employees_str})"


def has_permission(doc, ptype="read", user=None):
    if not user:
        user = frappe.session.user
        
    if user == "Administrator":
        return True
        
    if ptype != "read":
        # Let standard permissions handle write/submit/cancel
        return None
        
    roles = frappe.get_roles(user)
    admin_roles = ["HR Manager", "HR User", "Payroll Manager", "Payroll Administrator", "System Manager"]
    if any(role in roles for role in admin_roles):
        return True
        
    employee = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"})
    
    if not employee:
        return False
        
    # User can see their own slip
    if doc.employee == employee:
        return True
        
    # Check if doc.employee is a junior
    juniors = get_all_juniors(employee)
    if doc.employee in juniors:
        return True
        
    return False

def get_all_juniors(employee_name, visited=None):
    if visited is None:
        visited = set()
        
    if employee_name in visited:
        return []
        
    visited.add(employee_name)
    
    juniors = frappe.get_all("Employee", filters={"reports_to": employee_name, "status": "Active"}, pluck="name")
    all_juniors = list(juniors)
    for j in juniors:
        all_juniors.extend(get_all_juniors(j, visited))
    return list(set(all_juniors))
