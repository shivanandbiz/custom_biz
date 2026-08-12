import frappe

def create_web_form():
    form_name = "vendor-registration"
    if frappe.db.exists("Web Form", form_name):
        frappe.delete_doc("Web Form", form_name)

    doctype_name = "Vendor Registration Form"
    
    # Fetch all fields from the DocType to populate the Web Form
    meta = frappe.get_meta(doctype_name)
    
    web_form_fields = []
    skip_rest = False
    
    for field in meta.fields:
        # We don't want office use fields in the public form
        if field.fieldname == "section_office":
            skip_rest = True
            
        if skip_rest:
            continue
            
        web_form_fields.append({
            "fieldname": field.fieldname,
            "fieldtype": field.fieldtype,
            "label": field.label,
            "options": field.options,
            "reqd": field.reqd,
            "depends_on": field.depends_on,
            "description": field.description,
            "default": field.default,
            "hidden": field.hidden
        })

    custom_css = """
/* Premium Vendor Form Styling */

body {
    background-color: #f4f6f8;
    font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.web-form-wrapper {
    background: #ffffff;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    border-radius: 8px;
    padding: 50px;
    max-width: 900px;
    margin: 40px auto;
}

/* Header Text */
.web-form-header h1 {
    text-align: center;
    color: #1a365d;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.web-form-header .introduction {
    text-align: center;
    color: #e65100;
    font-size: 14px;
    font-weight: 600;
}

/* Numbered Section Headers */
body {
    counter-reset: section;
}

.section-heading, .web-form-page h4 {
    counter-increment: section;
    background-color: #1a365d !important;
    color: white !important;
    padding: 12px 15px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    margin-top: 40px !important;
    margin-bottom: 25px !important;
    display: flex;
    align-items: center;
    border-radius: 2px;
}

.section-heading::before, .web-form-page h4::before {
    content: counter(section);
    background-color: #e65100;
    color: white;
    min-width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    font-weight: 700;
}

/* Sub-section headings (if any) without numbers */
.section-heading.sub-heading {
    background-color: transparent !important;
    color: #1a365d !important;
    border-bottom: 2px solid #e65100;
    padding-left: 0 !important;
}
.section-heading.sub-heading::before {
    display: none;
}

/* Input Fields - Bottom Border Only */
.form-control {
    border: none !important;
    border-bottom: 1px solid #c4cdd5 !important;
    border-radius: 0 !important;
    background-color: transparent !important;
    box-shadow: none !important;
    padding: 8px 0 !important;
    color: #333 !important;
}
.form-control:focus {
    border-bottom: 2px solid #1a365d !important;
    box-shadow: none !important;
}

/* Labels */
.control-label {
    font-weight: 600 !important;
    color: #1a365d !important;
    font-size: 13px !important;
    margin-bottom: 0 !important;
}

/* Checkboxes */
.checkbox .label-area {
    font-weight: 500 !important;
    color: #444 !important;
}

/* Submit Button */
.btn-primary {
    background-color: #e65100 !important;
    border-color: #e65100 !important;
    font-weight: 600;
    padding: 10px 30px;
    border-radius: 4px;
    margin-top: 20px;
}
.btn-primary:hover {
    background-color: #cc4800 !important;
}
"""

    doc = frappe.get_doc({
        "doctype": "Web Form",
        "title": "Vendor Registration Form",
        "route": form_name,
        "doc_type": doctype_name,
        "module": "Custom Biz",
        "is_standard": 1,
        "published": 1,
        "login_required": 0,
        "allow_edit": 0,
        "allow_multiple": 0,
        "show_attachments": 1,
        "introduction_text": "<p style='text-align: center; color: #e65100;'>All Vendor Categories | Domestic (India) & International Vendors</p><p style='text-align: center; font-size: 12px;'>Please complete every section below. Sections marked with * are mandatory. Complete only the ONE category block in Step 7 that matches your business.</p>",
        "success_title": "Registration Submitted",
        "success_message": "Thank you for registering. Our team will review your application and contact you shortly.",
        "web_form_fields": web_form_fields,
        "custom_css": custom_css
    })
    
    doc.insert()
    print(f"Web Form '{doc.title}' created successfully at route '/{form_name}'")

def run():
    create_web_form()
    frappe.db.commit()

if __name__ == "__main__":
    run()
