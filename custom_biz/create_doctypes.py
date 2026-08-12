import frappe

def create_doctypes():
    create_vendor_poc()
    create_vendor_skill_set()
    create_vendor_kyc_document()
    create_vendor_registration()
    frappe.db.commit()

def create_vendor_poc():
    if not frappe.db.exists("DocType", "Vendor POC"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Custom Biz",
            "custom": 1,
            "istable": 1,
            "name": "Vendor POC",
            "fields": [
                {"fieldname": "first_name", "fieldtype": "Data", "label": "First Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "last_name", "fieldtype": "Data", "label": "Last Name", "in_list_view": 1},
                {"fieldname": "email_address", "fieldtype": "Data", "label": "Email Address", "options": "Email", "reqd": 1, "in_list_view": 1},
                {"fieldname": "phone_number", "fieldtype": "Data", "label": "Phone Number", "reqd": 1, "in_list_view": 1},
                {"fieldname": "designation", "fieldtype": "Data", "label": "Designation"}
            ]
        })
        doc.insert(ignore_permissions=True)

def create_vendor_skill_set():
    if not frappe.db.exists("DocType", "Vendor Skill Set"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Custom Biz",
            "custom": 1,
            "istable": 1,
            "name": "Vendor Skill Set",
            "fields": [
                {"fieldname": "technology", "fieldtype": "Data", "label": "Technology", "reqd": 1, "in_list_view": 1},
                {"fieldname": "experience_range", "fieldtype": "Data", "label": "Experience Range", "in_list_view": 1},
                {"fieldname": "salary_range", "fieldtype": "Data", "label": "Salary Range", "in_list_view": 1},
                {"fieldname": "location", "fieldtype": "Data", "label": "Location", "in_list_view": 1},
                {"fieldname": "mode_of_support", "fieldtype": "Select", "label": "Mode Of Support", "options": "\nOnsite\nRemote\nHybrid", "in_list_view": 1}
            ]
        })
        doc.insert(ignore_permissions=True)

def create_vendor_kyc_document():
    if not frappe.db.exists("DocType", "Vendor KYC Document"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Custom Biz",
            "custom": 1,
            "istable": 1,
            "name": "Vendor KYC Document",
            "fields": [
                {"fieldname": "document_type", "fieldtype": "Select", "label": "Document Type", "options": "\nCompany Profile\nRegistration Document\nPAN Card\nGST Registration\nCancelled Cheque\nID Proof\nOther", "reqd": 1, "in_list_view": 1},
                {"fieldname": "document_file", "fieldtype": "Attach", "label": "Document File", "reqd": 1, "in_list_view": 1}
            ]
        })
        doc.insert(ignore_permissions=True)

def create_vendor_registration():
    if not frappe.db.exists("DocType", "Vendor Registration"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "module": "Custom Biz",
            "custom": 1,
            "name": "Vendor Registration",
            "autoname": "VR-.YYYY.-.#####",
            "is_submittable": 1,
            "fields": [
                {"fieldname": "company_details_sec", "fieldtype": "Section Break", "label": "Company Details"},
                {"fieldname": "gstin_uin_number", "fieldtype": "Data", "label": "GSTIN / UIN Number", "depends_on": "eval:doc.country_of_operation == 'India'"},
                {"fieldname": "company_vendor_name", "fieldtype": "Data", "label": "Company/Vendor Name", "reqd": 1},
                {"fieldname": "vendor_group", "fieldtype": "Select", "label": "Vendor Group", "options": "\nServices\nIT & Non-IT Staffing Services\nTravel\nUPS\nUtility\nJob Portals\nFurniture\nHardware / IT\nCRM / ERP / Sitecore\nIndividual Contractor\nGeneral / Other", "reqd": 1},
                {"fieldname": "vendor_type", "fieldtype": "Select", "label": "Vendor Type", "options": "\nCompany\nPartnership\nProprietorship\nIndividual", "reqd": 1},
                {"fieldname": "country_of_operation", "fieldtype": "Link", "label": "Country of Operation", "options": "Country", "reqd": 1},
                
                {"fieldname": "india_statutory_details_sec", "fieldtype": "Section Break", "label": "India Statutory Details", "depends_on": "eval:doc.country_of_operation == 'India'"},
                {"fieldname": "pan_number", "fieldtype": "Data", "label": "PAN Number", "depends_on": "eval:doc.country_of_operation == 'India'"},
                {"fieldname": "gst_category", "fieldtype": "Select", "label": "GST Category", "options": "\nRegistered Regular\nRegistered Composition\nUnregistered\nSEZ\nOverseas\nDeemed Export\nUIN Holders", "depends_on": "eval:doc.country_of_operation == 'India'"},
                
                {"fieldname": "skill_set_sec", "fieldtype": "Section Break", "label": "Skill Set (Required for IT & Non-IT Staffing Services)", "depends_on": "eval:doc.vendor_group == 'IT & Non-IT Staffing Services' || doc.vendor_group == 'Individual Contractor'"},
                {"fieldname": "skill_set", "fieldtype": "Table", "label": "Skill Set", "options": "Vendor Skill Set"},
                
                {"fieldname": "primary_contact_person_sec", "fieldtype": "Section Break", "label": "Primary Contact Person"},
                {"fieldname": "primary_contact_details", "fieldtype": "Table", "label": "Primary Contact Details", "options": "Vendor POC"},
                
                {"fieldname": "primary_address_details_sec", "fieldtype": "Section Break", "label": "Primary Address Details"},
                {"fieldname": "preferred_billing_address", "fieldtype": "Check", "label": "Preferred Billing Address"},
                {"fieldname": "preferred_shipping_address", "fieldtype": "Check", "label": "Preferred Shipping Address"},
                {"fieldname": "address_line_1", "fieldtype": "Data", "label": "Address Line 1", "reqd": 1},
                {"fieldname": "address_line_2", "fieldtype": "Data", "label": "Address Line 2"},
                {"fieldname": "city", "fieldtype": "Data", "label": "City", "reqd": 1},
                {"fieldname": "state", "fieldtype": "Data", "label": "State / Province", "reqd": 1},
                {"fieldname": "postal_code", "fieldtype": "Data", "label": "Postal Code / Pincode", "reqd": 1},
                
                {"fieldname": "supporting_documents_sec", "fieldtype": "Section Break", "label": "Supporting Documents"},
                {"fieldname": "supporting_documents", "fieldtype": "Table", "label": "Supporting Documents", "options": "Vendor KYC Document"},
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
