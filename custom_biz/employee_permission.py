import frappe

def employee_has_permission(doc, ptype, user):
    if not doc or not user:
        return None
        
    if ptype == "write":
        user_id = getattr(doc, "user_id", None)
        if user_id and user_id == user:
            # Allow bypass for file operations on their own profile
            if getattr(frappe, "request", None):
                path = getattr(frappe.request, "path", "") or ""
                cmd = frappe.form_dict.get("cmd", "") if getattr(frappe, "form_dict", None) else ""
                
                is_upload = path.endswith('/upload_file') or cmd == 'upload_file'
                
                if is_upload:
                    return True
                
    return None

