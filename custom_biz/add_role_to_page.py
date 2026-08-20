import frappe

def run():
    page_name = "resource-workload-da"
    if not frappe.db.exists("Page", page_name):
        print("Page does not exist")
        return
        
    doc = frappe.get_doc("Page", page_name)
    has_role = False
    for r in doc.roles:
        if r.role in ["All", "Employee"]:
            has_role = True
            break
            
    if not has_role:
        doc.append("roles", {"role": "All"})
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print("Added 'All' role to Page")
    else:
        print("Role already exists")
