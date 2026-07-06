import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=True)
def register_vendor(data):
    """
    API endpoint to register a vendor and create Supplier, Address, and Contact records.
    `data` should be a JSON string or dictionary containing the form fields.
    """
    if isinstance(data, str):
        data = json.loads(data)

    # 1. Extract and validate mandatory fields
    supplier_name = data.get("supplier_name")
    first_name = data.get("first_name")
    email_id = data.get("email_id")
    
    if not supplier_name:
        frappe.throw(_("Company/Vendor Name is mandatory"))
    if not first_name:
        frappe.throw(_("Contact First Name is mandatory"))
    if not email_id:
        frappe.throw(_("Email ID is mandatory"))
        
    try:
        # 2. Create the Supplier Document
        supplier = frappe.new_doc("Supplier")
        supplier.supplier_name = supplier_name
        supplier.supplier_group = data.get("supplier_group", "All Supplier Groups")
        supplier.supplier_type = data.get("supplier_type", "Company")
        supplier.pan = data.get("pan")
        
        if data.get("gstin"):
            # Try setting gstin on supplier if the field exists
            try:
                supplier.gstin = data.get("gstin")
            except Exception:
                pass
        
        # Add Skill Set if Manpower Services
        custom_skill_set = data.get("custom_skill_set")
        if supplier.supplier_group == "Manpower Services" and custom_skill_set and isinstance(custom_skill_set, list):
            for row in custom_skill_set:
                tech = row.get("technology")
                if tech:
                    # Check if Skill exists, if not create it
                    if not frappe.db.exists("Skill", tech):
                        try:
                            frappe.get_doc({"doctype": "Skill", "skill_name": tech}).insert(ignore_permissions=True)
                        except Exception:
                            pass # If it fails, ignore
                
                supplier.append("custom_skill_set", {
                    "technology": tech,
                    "experience_range": row.get("experience_range"),
                    "salary_range": row.get("salary_range")
                })

        # Save without permissions checking if called by a guest (unauthenticated web form)
        supplier.save(ignore_permissions=True)
        
        # 3. Create the Address Document
        if data.get("address_line1") and data.get("city"):
            address = frappe.new_doc("Address")
            address.address_title = supplier_name
            address.address_type = "Billing"
            address.address_line1 = data.get("address_line1")
            address.address_line2 = data.get("address_line2")
            address.city = data.get("city")
            address.state = data.get("state")
            address.gst_state = data.get("state")
            address.country = data.get("country", "India")
            address.pincode = data.get("pincode")
            
            # Set Email and Phone directly on the Address
            address.email_id = email_id
            address.phone = data.get("phone")
            
            if data.get("preferred_billing_address"):
                address.is_primary_address = 1
            if data.get("preferred_shipping_address"):
                address.is_shipping_address = 1
            
            if data.get("gstin"):
                try:
                    address.gstin = data.get("gstin")
                except Exception:
                    pass
                    
            if data.get("gst_category"):
                try:
                    address.gst_category = data.get("gst_category")
                except Exception:
                    pass
                    
            # Calculate and Set Tax Category based on State
            company = frappe.db.get_single_value('Global Defaults', 'default_company')
            if not company:
                company = frappe.db.get_value("Company", filters=None, fieldname="name")
            
            company_state = ""
            if company:
                company_address_name = frappe.db.get_value("Dynamic Link", {"link_doctype": "Company", "link_name": company}, "parent")
                if company_address_name:
                    company_state = frappe.db.get_value("Address", company_address_name, "state")
                    
            if data.get("country", "India") == "India":
                vendor_state = str(data.get("state") or "").strip().lower()
                company_state_str = str(company_state or "").strip().lower()
                
                if vendor_state and company_state_str:
                    if vendor_state == company_state_str:
                        address.tax_category = "In-State"
                    else:
                        address.tax_category = "Out-State"
            
            # Link the Address to the new Supplier
            address.append("links", {
                "link_doctype": "Supplier",
                "link_name": supplier.name
            })
            address.save(ignore_permissions=True)
            
            # Set as primary address on Supplier if requested
            if data.get("preferred_billing_address"):
                supplier.supplier_primary_address = address.name
                from frappe.contacts.doctype.address.address import get_address_display
                supplier.primary_address = get_address_display(address.name)
            
        # 4. Handle Document Upload Attachment
        doc_base64 = data.get("vendor_document_base64")
        doc_name = data.get("vendor_document_name")
        if doc_base64 and doc_name:
            import base64
            from frappe.utils.file_manager import save_file
            
            # Clean base64 string
            if "," in doc_base64:
                doc_base64 = doc_base64.split(",")[1]
            
            try:
                file_bytes = base64.b64decode(doc_base64)
                save_file(
                    fname=doc_name,
                    content=file_bytes,
                    dt="Supplier",
                    dn=supplier.name,
                    is_private=1,
                    folder="Home/Attachments"
                )
            except Exception as e:
                frappe.log_error(f"Vendor Registration File Upload Error: {str(e)}", "Vendor Registration")

        # 5. Create the Contact Document
        contact = frappe.new_doc("Contact")
        contact.first_name = first_name
        contact.last_name = data.get("last_name")
        contact.is_primary_contact = 1
        
        # Add email
        contact.append("email_ids", {
            "email_id": email_id,
            "is_primary": 1
        })
        
        # Add phone
        phone = data.get("phone")
        if phone:
            contact.append("phone_nos", {
                "phone": phone,
                "is_primary_phone": 1
            })
            
        # Link the Contact to the new Supplier
        contact.append("links", {
            "link_doctype": "Supplier",
            "link_name": supplier.name
        })
        contact.save(ignore_permissions=True)
        
        # Automatically set as primary contact and display fields
        supplier.supplier_primary_contact = contact.name
        supplier.email_id = email_id
        supplier.mobile_no = phone
        
        # Save the supplier again so that Frappe triggers the 'set_primary_address' 
        # and 'set_primary_contact' logic to generate the formatted HTML display texts.
        supplier.save(ignore_permissions=True)

        # 6. Commit the transaction
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": _("Vendor registered successfully!"),
            "supplier_id": supplier.name
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Vendor Registration Error")
        return {
            "status": "error",
            "message": str(e)
        }

import frappe
def create_page():
    if not frappe.db.exists("Page", "SmartHR Admin Dashboard"):
        doc = frappe.get_doc({
            "doctype": "Page",
            "page_name": "SmartHR Admin Dashboard",
            "title": "SmartHR Admin Dashboard",
            "module": "Custom Biz",
            "standard": "Yes",
            "roles": [{"role": "System Manager"}]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Page created successfully")
    else:
        print("Page already exists")
