import frappe
import json
from custom_biz.api.vendor_registration_api import submit_vendor_registration

@frappe.whitelist()
def run():
    data_obj = {
        "vendor_category": "HR / Staffing Partner",
        "vendor_type": "Company",
        "company_vendor_name": "Alpha E2E Test Supplier Ltd",
        "country_of_operation": "India",
        "pan_number": "ABCDE1234F",
        "gst_category": "Registered",
        "billing_address_line_1": "123 Alpha St",
        "billing_city": "Mumbai",
        "billing_state": "Maharashtra",
        "billing_postal_code": "400001",
        "billing_country": "India",
        "bank_name": "Test Bank",
        "account_number": "9876543210",
        "account_holder_name": "Alpha E2E Test Supplier Ltd",
        "ifsc_code": "TEST0001234",
        "poc_details": [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "designation": "Manager",
                "email_address": "alice@alphatest.com",
                "phone_number": "9876543210"
            }
        ]
    }
    
    res = submit_vendor_registration(json.dumps(data_obj))
    if res.get("status") != "success":
        return "Failed: " + str(res)
    
    vr_name = res.get("name")
    vr = frappe.get_doc("Vendor Registration Form", vr_name)
    
    output = []
    output.append(f"POC Count: {len(vr.poc_details)}")
    if vr.poc_details:
        output.append(f"POC Email: {vr.poc_details[0].email_address}")
        
    supplier = frappe.get_all("Supplier", filters={"supplier_name": "Alpha E2E Test Supplier Ltd"}, limit=1)
    if supplier:
        sup_doc = frappe.get_doc("Supplier", supplier[0].name)
        output.append(f"Found Supplier: {sup_doc.name}")
        output.append(f"Supplier Group: {sup_doc.supplier_group}")
        output.append(f"Tax ID: {getattr(sup_doc, 'tax_id', getattr(sup_doc, 'pan', None))}")
        
        bank = frappe.get_all("Bank Account", filters={"party": sup_doc.name}, limit=1)
        if bank:
            output.append(f"Found Bank Account: {bank[0].name}")
            
        contact = frappe.get_all("Dynamic Link", filters={"link_doctype": "Supplier", "link_name": sup_doc.name, "parenttype": "Contact"}, fields=["parent"])
        if contact:
            output.append(f"Found Contact: {contact[0].parent}")
            
        address = frappe.get_all("Dynamic Link", filters={"link_doctype": "Supplier", "link_name": sup_doc.name, "parenttype": "Address"}, fields=["parent"])
        if address:
            output.append(f"Found Address: {address[0].parent}")
    else:
        output.append("Supplier NOT CREATED.")
        
    return "\\n".join(output)

