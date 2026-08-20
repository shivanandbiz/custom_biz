import frappe

def get_or_create_employee_folder(folder_name):
    """
    Creates and secures an Employee folder under 'Home/' in a version-agnostic manner.
    Compatible with Frappe v13, v14, v15, and v16.
    """
    folder_name = folder_name.strip()
    expected_folder_id = f"Home/{folder_name}"

    if not frappe.db.exists("File", expected_folder_id):
        try:
            # Method 1: Standard Frappe create_new_folder helper
            try:
                from frappe.core.api.file import create_new_folder
                folder_doc = create_new_folder(folder_name, "Home")
            except ImportError:
                from frappe.core.doctype.file.file import create_new_folder
                folder_doc = create_new_folder(folder_name, "Home")
            
            if folder_doc:
                folder_doc.is_private = 1
                folder_doc.save(ignore_permissions=True)
        except Exception:
            # Method 2: Direct DocType insertion fallback (Universal across all Frappe versions)
            if not frappe.db.exists("File", expected_folder_id):
                try:
                    folder_doc = frappe.get_doc({
                        "doctype": "File",
                        "file_name": folder_name,
                        "is_folder": 1,
                        "folder": "Home",
                        "is_private": 1
                    })
                    folder_doc.insert(ignore_permissions=True)
                except Exception:
                    pass  # Handled race condition or concurrent creation

    return expected_folder_id


def file_before_insert(doc, method=None):
    # Skip for folders
    if getattr(doc, "is_folder", 0):
        return

    target_employee_name = None
    target_user = None

    attached_to_doctype = getattr(doc, "attached_to_doctype", None)
    attached_to_name = getattr(doc, "attached_to_name", None)

    # If attaching directly to an Employee profile, use that Employee's folder
    if attached_to_doctype == "Employee" and attached_to_name:
        target_employee_name = frappe.db.get_value("Employee", attached_to_name, "employee_name")
        target_user = frappe.db.get_value("Employee", attached_to_name, "user_id")
        doc.is_private = 1  # Employee attachments should always be private
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

    doc.folder = get_or_create_employee_folder(folder_name)


def file_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user
    if user == "Administrator":
        return ""
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "HR Manager" in roles or "HR User" in roles:
        return ""
        
    employee_name = frappe.db.get_value("Employee", {"user_id": user}, "employee_name")
    employee_id = frappe.db.get_value("Employee", {"user_id": user}, "name")

    conditions = [
        "`tabFile`.is_private = 0",
        f"`tabFile`.owner = {frappe.db.escape(user)}"
    ]

    # Allow non-Employee attachments (e.g. attached to Tasks, Projects, Expenses, etc.)
    conditions.append("(`tabFile`.attached_to_doctype IS NOT NULL AND `tabFile`.attached_to_doctype != 'Employee')")

    if employee_id:
        conditions.append(f"(`tabFile`.attached_to_doctype = 'Employee' AND `tabFile`.attached_to_name = {frappe.db.escape(employee_id)})")

    if employee_name:
        my_folder = f"Home/{employee_name.strip()}"
        conditions.append(f"`tabFile`.folder = {frappe.db.escape(my_folder)}")
        conditions.append(f"`tabFile`.name = {frappe.db.escape(my_folder)}")

    return f"({' OR '.join(conditions)})"


def file_has_permission(doc, ptype="read", user=None):
    if not doc:
        return None

    if not user:
        user = frappe.session.user
    if user == "Administrator":
        return True
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "HR Manager" in roles or "HR User" in roles:
        return True  # Explicitly allow access for HR & Admins

    is_private = getattr(doc, "is_private", doc.get("is_private") if isinstance(doc, dict) else 0)
    owner = getattr(doc, "owner", doc.get("owner") if isinstance(doc, dict) else None)
    folder = getattr(doc, "folder", doc.get("folder") if isinstance(doc, dict) else None)
    name = getattr(doc, "name", doc.get("name") if isinstance(doc, dict) else None)
    attached_to_doctype = getattr(doc, "attached_to_doctype", doc.get("attached_to_doctype") if isinstance(doc, dict) else None)
    attached_to_name = getattr(doc, "attached_to_name", doc.get("attached_to_name") if isinstance(doc, dict) else None)

    if is_private == 0:
        return None  # Public files follow standard permissions
        
    if owner == user:
        return None  # File owner follows standard permissions

    employee = frappe.db.get_value("Employee", {"user_id": user}, ["name", "employee_name"], as_dict=True)
    
    if employee:
        # Allow access if attached directly to their own Employee record
        if attached_to_doctype == "Employee" and attached_to_name == employee.name:
            return True

        # Allow access if file is inside their personal employee folder
        my_folder = f"Home/{employee.employee_name.strip()}"
        if folder == my_folder or name == my_folder:
            return True

    # Check if attached to another document (e.g. Task, Project, Leave, etc.) that the user has permission to view
    if attached_to_doctype and attached_to_name and attached_to_doctype != "Employee":
        if frappe.has_permission(attached_to_doctype, ptype, attached_to_name, user=user):
            return True

    # Explicitly deny access to private files stored in another employee's folder
    if folder and folder.startswith("Home/") and folder != "Home":
        return False

    # Fallback to standard Frappe permission check for any other file
    return None


@frappe.whitelist()
def migrate_existing_files():
    frappe.only_for("System Manager")
    
    # Get all files that are not folders
    files = frappe.get_all("File", 
                           filters={"is_folder": 0}, 
                           fields=["name", "owner", "folder", "attached_to_doctype", "attached_to_name"])
    count = 0
    
    for f in files:
        target_employee_name = None
        target_user = None

        if f.attached_to_doctype == "Employee" and f.attached_to_name:
            target_employee_name = frappe.db.get_value("Employee", f.attached_to_name, "employee_name")
            target_user = frappe.db.get_value("Employee", f.attached_to_name, "user_id")
        else:
            target_user = f.owner
            if target_user == "Administrator" or not target_user:
                continue
            target_employee_name = frappe.db.get_value("Employee", {"user_id": target_user}, "employee_name")
        
        if target_employee_name:
            folder_name = target_employee_name
        elif target_user:
            folder_name = frappe.db.get_value("User", target_user, "full_name") or target_user
        else:
            continue

        expected_folder_id = get_or_create_employee_folder(folder_name)
        
        # Skip if already in the right folder
        if f.folder == expected_folder_id:
            continue
            
        # Move file to the new folder
        frappe.db.set_value("File", f.name, "folder", expected_folder_id)
        count += 1
        
    frappe.db.commit()
    print(f"Successfully migrated {count} files to their respective employee folders.")
    return count
