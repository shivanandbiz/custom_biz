import frappe

def test():
    if not frappe.db.exists("Country", "India"):
        frappe.get_doc({"doctype": "Country", "country_name": "India"}).insert(ignore_permissions=True)
        
    doc = frappe.get_doc({
        "doctype": "Vendor Registration",
        "company_vendor_name": "Test Vendor LLC",
        "vendor_group": "Services",
        "vendor_type": "Company",
        "country_of_operation": "India",
        "address_line_1": "123 Test St",
        "city": "Bangalore",
        "state": "Karnataka",
        "postal_code": "560001",
        "pan_number": "ABCDE1234F"
    })
    doc.insert(ignore_permissions=True)
    
    # Trigger workflow approval which submits it
    frappe.msgprint(f"Created Vendor Registration: {doc.name}")
