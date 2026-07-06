import frappe

def create_page():
    if not frappe.db.exists("Page", "SmartHR Admin Dashboard"):
        doc = frappe.get_doc({
            "doctype": "Page",
            "page_name": "SmartHR Admin Dashboard",
            "title": "SmartHR Admin Dashboard",
            "module": "Custom Biz",
            "standard": "Yes",
            "roles": [
                {
                    "role": "System Manager"
                }
            ]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Page created successfully")
    else:
        print("Page already exists")

