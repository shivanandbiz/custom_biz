import frappe
from frappe.model.mapper import get_mapped_doc
import json

def on_submit(doc, method):
    # This is triggered when the Vendor Registration is Approved (Submitted)
    supplier = frappe.new_doc("Supplier")
    supplier.supplier_name = doc.company_vendor_name
    supplier.supplier_group = doc.vendor_category if frappe.db.exists("Supplier Group", doc.vendor_category) else "All Supplier Groups"
    supplier.supplier_type = doc.vendor_type
    supplier.country = doc.country_of_operation
    
    # Specifics for India
    if doc.country_of_operation == "India":
        supplier.pan = doc.pan_number
        if doc.gst_category:
            supplier.gst_category = doc.gst_category
            
    supplier.insert(ignore_permissions=True)
    
    # Create Primary Address
    primary_address_name = None
    if doc.billing_address_line_1 or doc.billing_city:
        address = frappe.new_doc("Address")
        address.address_title = doc.company_vendor_name
        address.address_type = "Billing"
        address.address_line1 = doc.billing_address_line_1
        address.address_line2 = doc.billing_address_line_2
        address.city = doc.billing_city
        address.state = doc.billing_state
        address.pincode = doc.billing_postal_code
        address.country = doc.billing_country
        address.is_primary_address = 1
        if doc.same_as_billing_address:
            address.is_shipping_address = 1
        
        # Link Address to Supplier
        address.append("links", {
            "link_doctype": "Supplier",
            "link_name": supplier.name
        })
        
        if doc.gstin_uin_number:
            address.gstin = doc.gstin_uin_number
            
        address.insert(ignore_permissions=True)
        primary_address_name = address.name
        supplier.db_set("supplier_primary_address", primary_address_name)

    # Shipping Address if different
    if not doc.same_as_billing_address and (doc.shipping_address_line_1 or doc.shipping_city):
        ship_addr = frappe.new_doc("Address")
        ship_addr.address_title = doc.company_vendor_name + " - Shipping"
        ship_addr.address_type = "Shipping"
        ship_addr.address_line1 = doc.shipping_address_line_1
        ship_addr.address_line2 = doc.shipping_address_line_2
        ship_addr.city = doc.shipping_city
        ship_addr.state = doc.shipping_state
        ship_addr.pincode = doc.shipping_postal_code
        ship_addr.country = doc.shipping_country
        ship_addr.is_shipping_address = 1
        ship_addr.append("links", {
            "link_doctype": "Supplier",
            "link_name": supplier.name
        })
        ship_addr.insert(ignore_permissions=True)

    # Create Primary Contacts
    primary_contact_name = None
    first_contact_name = None
    for poc in doc.get("poc_details", []):
        contact = frappe.new_doc("Contact")
        contact.first_name = poc.first_name
        contact.last_name = poc.last_name
        contact.designation = poc.designation
        contact.append("email_ids", {
            "email_id": poc.email_address,
            "is_primary": 1
        })
        contact.append("phone_nos", {
            "phone": poc.phone_number,
            "is_primary_phone": 1
        })
        if poc.get("poc_type"):
            contact.department = poc.poc_type
        if poc.get("is_primary"):
            contact.is_primary_contact = 1
        
        # Link Contact to Supplier
        contact.append("links", {
            "link_doctype": "Supplier",
            "link_name": supplier.name
        })
        
        contact.insert(ignore_permissions=True)
        if not first_contact_name:
            first_contact_name = contact.name
        if poc.get("is_primary") and not primary_contact_name:
            primary_contact_name = contact.name
            
    if not primary_contact_name and first_contact_name:
        primary_contact_name = first_contact_name
        
    if primary_contact_name:
        supplier.db_set("supplier_primary_contact", primary_contact_name)
        
    # Also add Bank Details if applicable
    if doc.bank_name and doc.account_number:
        # Check if Bank exists, if not create it
        if not frappe.db.exists("Bank", doc.bank_name):
            bank = frappe.new_doc("Bank")
            bank.bank_name = doc.bank_name
            bank.insert(ignore_permissions=True)
            
        # Bank Account creation
        bank_account = frappe.new_doc("Bank Account")
        bank_account.party_type = "Supplier"
        bank_account.party = supplier.name
        bank_account.bank = doc.bank_name
        bank_account.bank_account_no = doc.account_number
        bank_account.account_name = doc.account_holder_name
        bank_account.branch_code = doc.ifsc_code or doc.swift_iban
        bank_account.is_default = 1
        bank_account.insert(ignore_permissions=True)
        
    frappe.msgprint(f"Supplier {supplier.name} has been successfully created.")

@frappe.whitelist(allow_guest=True)
def submit_vendor_registration(data):
    try:
        doc_data = json.loads(data)
        doc_data["doctype"] = "Vendor Registration"
        
        # If the user expects it to instantly submit and create supplier, we set docstatus=1.
        # But usually we just insert as draft. Let's insert as submitted so the on_submit hook fires.
        doc_data["docstatus"] = 1
        
        doc = frappe.get_doc(doc_data)
        doc.insert(ignore_permissions=True)
        # doc.submit() is not needed since docstatus=1 is set before insert in Frappe? No, insert() sets it to 0 if we don't call submit().
        # Actually, let's call doc.submit() instead to properly trigger on_submit hooks.
        
        if hasattr(frappe.request, 'files') and frappe.request.files:
            for fieldname, file_storage in frappe.request.files.items():
                if fieldname.startswith('file_') and file_storage.filename:
                    file_content = file_storage.read()
                    file_doc = frappe.get_doc({
                        "doctype": "File",
                        "file_name": file_storage.filename,
                        "content": file_content,
                        "attached_to_doctype": doc.doctype,
                        "attached_to_name": doc.name,
                        "is_private": 1
                    })
                    file_doc.insert(ignore_permissions=True)

        doc.submit()

        frappe.db.commit()
        
        return {"status": "success", "message": "Registration submitted successfully!", "name": doc.name}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Vendor Registration Error", message=str(e) + "\n" + frappe.get_traceback())
        return {"status": "error", "message": str(e)}
