import frappe
import json

def create_web_form():
    if not frappe.db.exists("Web Form", "Vendor Registration Form"):
        doc = frappe.get_doc({
            "doctype": "Web Form",
            "module": "Custom Biz",
            "title": "Vendor Registration Form",
            "route": "vendor-registration",
            "doc_type": "Vendor Registration",
            "is_standard": 1,
            "published": 1,
            "login_required": 0,
            "allow_multiple": 1,
            "allow_edit": 0,
            "show_sidebar": 0,
            "introduction_text": "Complete the form below to register your business and join our elite network of global vendors.",
            "button_label": "Submit Registration",
            "client_script": """
frappe.web_form.on('country_of_operation', (field, value) => {
    if (value === 'India') {
        frappe.web_form.set_df_property('india_statutory_details_sec', 'hidden', 0);
        frappe.web_form.set_df_property('gstin_uin_number', 'hidden', 0);
        frappe.web_form.set_df_property('pan_number', 'hidden', 0);
        frappe.web_form.set_df_property('gst_category', 'hidden', 0);
    } else {
        frappe.web_form.set_df_property('india_statutory_details_sec', 'hidden', 1);
        frappe.web_form.set_df_property('gstin_uin_number', 'hidden', 1);
        frappe.web_form.set_df_property('pan_number', 'hidden', 1);
        frappe.web_form.set_df_property('gst_category', 'hidden', 1);
    }
});

frappe.web_form.on('vendor_group', (field, value) => {
    if (value === 'IT & Non-IT Staffing Services' || value === 'Individual Contractor') {
        frappe.web_form.set_df_property('skill_set_sec', 'hidden', 0);
        frappe.web_form.set_df_property('skill_set', 'hidden', 0);
    } else {
        frappe.web_form.set_df_property('skill_set_sec', 'hidden', 1);
        frappe.web_form.set_df_property('skill_set', 'hidden', 1);
    }
});
""",
            "custom_css": """
.web-form-page {
    background-color: #f4f6f8;
    padding: 20px;
    border-radius: 8px;
}
.web-form-header h1 {
    color: #1a4273;
    font-weight: 700;
    text-align: center;
}
.web-form-wrapper {
    background: #eef3f8;
    border: 1px solid #d1d9e6;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}
.btn-primary {
    background-color: #f47f24;
    border-color: #f47f24;
    font-weight: bold;
    padding: 10px 30px;
    border-radius: 20px;
}
""",
            "web_form_fields": [
                {"fieldname": "company_details_sec", "fieldtype": "Section Break", "label": "Company Details"},
                {"fieldname": "gstin_uin_number", "fieldtype": "Data", "label": "GSTIN / UIN Number"},
                {"fieldname": "company_vendor_name", "fieldtype": "Data", "label": "Company/Vendor Name", "reqd": 1},
                {"fieldname": "vendor_group", "fieldtype": "Select", "label": "Vendor Group", "reqd": 1},
                {"fieldname": "vendor_type", "fieldtype": "Select", "label": "Vendor Type", "reqd": 1},
                {"fieldname": "country_of_operation", "fieldtype": "Link", "label": "Country of Operation", "options": "Country", "reqd": 1},
                
                {"fieldname": "india_statutory_details_sec", "fieldtype": "Section Break", "label": "India Statutory Details"},
                {"fieldname": "pan_number", "fieldtype": "Data", "label": "PAN Number"},
                {"fieldname": "gst_category", "fieldtype": "Select", "label": "GST Category"},
                
                {"fieldname": "skill_set_sec", "fieldtype": "Section Break", "label": "Skill Set (Required for IT & Non-IT Staffing Services)"},
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
            ]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
