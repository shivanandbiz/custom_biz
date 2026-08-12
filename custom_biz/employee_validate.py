import frappe

def employee_validate(doc, method):
    user = frappe.session.user
    if user == "Administrator":
        return
        
    roles = frappe.get_roles(user)
    if "System Manager" in roles or "HR Manager" in roles or "HR User" in roles:
        return
        
    # If a standard Employee is trying to save their own profile
    if doc.user_id == user and not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if old_doc:
            # Check if they changed anything important
            for key, value in doc.as_dict().items():
                # Allow them to only update their profile picture, nothing else!
                if key not in ['modified', 'modified_by', 'image'] and not key.startswith('_'):
                    if old_doc.get(key) != value:
                        frappe.throw(f"Employees are not allowed to edit their HR profile fields (You tried to change: {key}). You may only upload files.")
