import frappe

def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
        
    if user == "Administrator":
        return ""
        
    roles = frappe.get_roles(user)
    # Only Admin (System Manager) can see all salary slips
    if "System Manager" in roles:
        return ""
        
    # Get active employee linked to the user
    employee = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"})
    
    if not employee:
        # If user is not an employee and has no admin roles, they shouldn't see any
        return "1=0"
        
    employee_escaped = frappe.db.escape(employee)
    return f"`tabSalary Slip`.employee = {employee_escaped}"


def has_permission(doc, ptype="read", user=None):
    if not user:
        user = frappe.session.user
        
    if user == "Administrator":
        return True
        
    if ptype != "read":
        # Let standard permissions handle write/submit/cancel
        return None
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles:
        return True
        
    employee = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"})
    
    if not employee:
        return False
        
    # User can see their own slip
    if doc.employee == employee:
        return True
        
    return False
