import frappe

def employee_has_permission(doc, ptype, user):
    if not doc or not user:
        return None
        
    if ptype == "write":
        print(f"DEBUG: Checking write permission for {doc.name}. User: {user}, Doc User ID: {doc.user_id}")
        if doc.user_id == user:
            # Allow bypass for file operations on their own profile
            if frappe.request:
                path = frappe.request.path or ""
                cmd = frappe.form_dict.get("cmd", "")
                print(f"DEBUG: Path: {path}, Cmd: {cmd}")
                
                is_upload = path.endswith('/upload_file') or cmd == 'upload_file'
                print(f"DEBUG: Is Upload: {is_upload}")
                
                if is_upload:
                    return True
                
    return None
