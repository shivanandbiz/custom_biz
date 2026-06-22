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
            address.country = data.get("country", "India")
            address.pincode = data.get("pincode")
            
            if data.get("gstin"):
                try:
                    address.gstin = data.get("gstin")
                except Exception:
                    pass
            
            # Link the Address to the new Supplier
            address.append("links", {
                "link_doctype": "Supplier",
                "link_name": supplier.name
            })
            address.save(ignore_permissions=True)
            
        # 4. Create the Contact Document
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

        # 5. Commit the transaction
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
