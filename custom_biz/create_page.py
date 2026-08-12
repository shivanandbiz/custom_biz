import frappe

def run():
    page_name = "Intervals Dashboard"
    if not frappe.db.exists("Page", page_name):
        doc = frappe.new_doc("Page")
        doc.page_name = page_name
        doc.title = "Intervals Dashboard"
        doc.module = "Custom Biz"
        doc.standard = "Yes"
        doc.insert(ignore_permissions=True)
        print("Page created successfully")
    else:
        print("Page already exists")
