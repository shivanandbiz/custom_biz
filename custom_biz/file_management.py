import frappe

def file_before_insert(doc, method):
    # Skip for folders
    if doc.is_folder:
        return

    target_employee_name = None
    target_user = None

    # If attaching directly to an Employee profile, use that Employee's folder
    if doc.attached_to_doctype == "Employee" and doc.attached_to_name:
        target_employee_name = frappe.db.get_value("Employee", doc.attached_to_name, "employee_name")
        target_user = frappe.db.get_value("Employee", doc.attached_to_name, "user_id")
    else:
        # Otherwise, use the folder of the person uploading
        target_user = frappe.session.user
        if target_user == "Administrator" or not target_user:
            return
        target_employee_name = frappe.db.get_value("Employee", {"user_id": target_user}, "employee_name")
    
    if target_employee_name:
        folder_name = target_employee_name
    elif target_user:
        # Fallback to User full name
        folder_name = frappe.db.get_value("User", target_user, "full_name") or target_user
    else:
        return

    expected_folder_id = f"Home/{folder_name}"

    if not frappe.db.exists("File", expected_folder_id):
        # Create folder
        folder_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": folder_name,
            "is_folder": 1,
            "folder": "Home",
            "is_private": 1
        })
        folder_doc.insert(ignore_permissions=True)
    
    doc.folder = expected_folder_id

def file_permission_query_conditions(user):
    if not user:
        user = frappe.session.user
    if user == "Administrator":
        return ""
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "HR Manager" in roles or "HR User" in roles:
        return ""
        
    employee_name = frappe.db.get_value("Employee", {"user_id": user}, "employee_name")
    if employee_name:
        my_folder = f"Home/{employee_name}"
        return f"(`tabFile`.is_private = 0 OR `tabFile`.owner = {frappe.db.escape(user)} OR `tabFile`.folder = {frappe.db.escape(my_folder)})"
        
    # Restrict users to only see public files or files they uploaded
    return f"(`tabFile`.is_private = 0 OR `tabFile`.owner = {frappe.db.escape(user)})"

def file_has_permission(doc, ptype, user):
    if not doc:
        return None

    if not user:
        user = frappe.session.user
    if user == "Administrator":
        return True
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "HR Manager" in roles or "HR User" in roles:
        return None # Fallback to standard permissions
        
    if doc.is_private == 0:
        return None # Fallback to standard permissions for public files
        
    if doc.owner == user:
        return None # Fallback to standard permissions for their own files
        
    employee_name = frappe.db.get_value("Employee", {"user_id": user}, "employee_name")
    if employee_name and doc.folder == f"Home/{employee_name}":
        return None # Fallback to standard permissions for files in their own folder
        
    # Explicitly deny access to private files not owned by them
    return False

@frappe.whitelist()
def migrate_existing_files():
    frappe.only_for("System Manager")
    
    # Get all files not uploaded by Administrator
    files = frappe.get_all("File", 
                           filters={"is_folder": 0, "owner": ["!=", "Administrator"]}, 
                           fields=["name", "owner", "folder"])
    count = 0
    
    for f in files:
        user = f.owner
        
        employee_name = frappe.db.get_value("Employee", {"user_id": user}, "employee_name")
        if employee_name:
            folder_name = employee_name
        else:
            folder_name = frappe.db.get_value("User", user, "full_name") or user

        expected_folder_id = f"Home/{folder_name}"
        
        # Skip if already in the right folder
        if f.folder == expected_folder_id:
            continue
            
        # Create folder if it doesn't exist
        if not frappe.db.exists("File", expected_folder_id):
            folder_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": folder_name,
                "is_folder": 1,
                "folder": "Home",
                "is_private": 1
            })
            folder_doc.insert(ignore_permissions=True)
            
        # Move file to the new folder
        frappe.db.set_value("File", f.name, "folder", expected_folder_id)
        count += 1
        
    frappe.db.commit()
    print(f"Successfully migrated {count} files to their respective employee folders.")
    return count

