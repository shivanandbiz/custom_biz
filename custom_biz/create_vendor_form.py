import frappe

def create_child_table_poc():
    doctype_name = "Vendor POC"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Custom Biz",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "poc_name", "label": "Name", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "email", "label": "Email", "fieldtype": "Data", "options": "Email", "in_list_view": 1},
                {"fieldname": "phone", "label": "Phone", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "poc_type", "label": "POC Type", "fieldtype": "Data", "description": "Sales / Finance & Billing / Operations & Support / Escalation", "in_list_view": 1},
                {"fieldname": "is_primary", "label": "Primary?", "fieldtype": "Check", "in_list_view": 1}
            ]
        })
        doc.insert()
        print(f"DocType '{doctype_name}' created.")
    else:
        print(f"DocType '{doctype_name}' already exists.")

def create_child_table_hr_skill():
    doctype_name = "Vendor HR Skill"
    if not frappe.db.exists("DocType", doctype_name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Custom Biz",
            "custom": 1,
            "istable": 1,
            "fields": [
                {"fieldname": "technology_skill", "label": "Technology / Skill", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "experience_range", "label": "Experience Range", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "salary_range", "label": "Salary Range", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "location", "label": "Location", "fieldtype": "Data", "in_list_view": 1},
                {"fieldname": "mode_of_support", "label": "Mode of Support", "fieldtype": "Data", "in_list_view": 1}
            ]
        })
        doc.insert()
        print(f"DocType '{doctype_name}' created.")
    else:
        print(f"DocType '{doctype_name}' already exists.")

def create_main_doctype():
    doctype_name = "Vendor Registration Form"
    if not frappe.db.exists("DocType", doctype_name):
        fields = [
            # 1 VENDOR CATEGORY & VENDOR TYPE
            {"fieldname": "section_1", "label": "Vendor Category & Vendor Type", "fieldtype": "Section Break"},
            {"fieldname": "vendor_category", "label": "Vendor Category", "fieldtype": "Select", "options": "\nHR / Staffing Partner\nTravel Vendor\nUPS / Power Backup Vendor\nWater & Utility Vendor\nJob Portal / Recruitment Platform\nFurniture Vendor\nIT Hardware & Software Vendor\nIndividual Contractor / Consultant\nGeneral / Other", "reqd": 1},
            {"fieldname": "cb_1", "fieldtype": "Column Break"},
            {"fieldname": "vendor_type", "label": "Vendor Type", "fieldtype": "Select", "options": "\nCompany\nProprietorship\nPartnership / LLP\nIndividual", "reqd": 1},
            
            # 2 COMPANY / VENDOR DETAILS
            {"fieldname": "section_2", "label": "Company / Vendor Details", "fieldtype": "Section Break"},
            {"fieldname": "company_vendor_name", "label": "Company / Vendor Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "trade_name", "label": "Trade Name (if different)", "fieldtype": "Data"},
            {"fieldname": "country_of_operation", "label": "Country of Operation", "fieldtype": "Link", "options": "Country", "reqd": 1},
            {"fieldname": "currency_of_transaction", "label": "Currency of Transaction", "fieldtype": "Link", "options": "Currency"},
            {"fieldname": "cb_2", "fieldtype": "Column Break"},
            {"fieldname": "website", "label": "Website", "fieldtype": "Data"},
            {"fieldname": "year_of_establishment", "label": "Year of Establishment", "fieldtype": "Data"},
            {"fieldname": "number_of_employees", "label": "Number of Employees (approx.)", "fieldtype": "Int"},
            {"fieldname": "nature_of_business", "label": "Nature of Business", "fieldtype": "Small Text"},

            # 3 STATUTORY / TAX DETAILS
            {"fieldname": "section_3", "label": "Statutory / Tax Details", "fieldtype": "Section Break"},
            {"fieldname": "india_details", "label": "India Statutory Details", "fieldtype": "Section Break", "depends_on": "eval:doc.country_of_operation == 'India'"},
            {"fieldname": "gstin_uin_number", "label": "GSTIN / UIN Number", "fieldtype": "Data"},
            {"fieldname": "pan_number", "label": "PAN Number", "fieldtype": "Data"},
            {"fieldname": "gst_category", "label": "GST Category", "fieldtype": "Select", "options": "\nRegistered\nUnregistered\nComposition"},
            {"fieldname": "cb_3a", "fieldtype": "Column Break"},
            {"fieldname": "tan", "label": "TAN", "fieldtype": "Data"},
            {"fieldname": "udyam_msme_reg_no", "label": "Udyam / MSME Reg. No.", "fieldtype": "Data"},

            {"fieldname": "international_details", "label": "International Statutory Details", "fieldtype": "Section Break", "depends_on": "eval:doc.country_of_operation && doc.country_of_operation != 'India'"},
            {"fieldname": "tax_id_vat_ein_number", "label": "Tax ID / VAT / EIN Number", "fieldtype": "Data"},
            {"fieldname": "company_registration_no", "label": "Company Registration / Incorporation No.", "fieldtype": "Data"},

            # 4 POINT(S) OF CONTACT (POC)
            {"fieldname": "section_4", "label": "Point(s) of Contact (POC)", "fieldtype": "Section Break"},
            {"fieldname": "poc_details", "label": "POC Details", "fieldtype": "Table", "options": "Vendor POC"},

            # 5 ADDRESS DETAILS
            {"fieldname": "section_5", "label": "Address Details", "fieldtype": "Section Break"},
            {"fieldname": "billing_address", "label": "Registered / Billing Address", "fieldtype": "Section Break"},
            {"fieldname": "billing_address_line_1", "label": "Address Line 1", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "billing_address_line_2", "label": "Address Line 2", "fieldtype": "Data"},
            {"fieldname": "billing_city", "label": "City", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "cb_5a", "fieldtype": "Column Break"},
            {"fieldname": "billing_state", "label": "State / Province", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "billing_postal_code", "label": "Postal / ZIP Code", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "billing_country", "label": "Country", "fieldtype": "Link", "options": "Country", "reqd": 1},

            {"fieldname": "shipping_address_section", "label": "Shipping / Service Address", "fieldtype": "Section Break"},
            {"fieldname": "same_as_billing_address", "label": "Same as Billing Address", "fieldtype": "Check"},
            {"fieldname": "sb_ship", "fieldtype": "Section Break", "depends_on": "eval:!doc.same_as_billing_address"},
            {"fieldname": "shipping_address_line_1", "label": "Address Line 1", "fieldtype": "Data"},
            {"fieldname": "shipping_address_line_2", "label": "Address Line 2", "fieldtype": "Data"},
            {"fieldname": "shipping_city", "label": "City", "fieldtype": "Data"},
            {"fieldname": "cb_5b", "fieldtype": "Column Break"},
            {"fieldname": "shipping_state", "label": "State / Province", "fieldtype": "Data"},
            {"fieldname": "shipping_postal_code", "label": "Postal / ZIP Code", "fieldtype": "Data"},
            {"fieldname": "shipping_country", "label": "Country", "fieldtype": "Link", "options": "Country"},

            # 6 BANK ACCOUNT DETAILS
            {"fieldname": "section_6", "label": "Bank Account Details", "fieldtype": "Section Break"},
            {"fieldname": "bank_name", "label": "Bank Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "account_holder_name", "label": "Account Holder / Beneficiary Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "account_number", "label": "Account Number", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "cb_6", "fieldtype": "Column Break"},
            {"fieldname": "ifsc_code", "label": "IFSC Code (India)", "fieldtype": "Data"},
            {"fieldname": "swift_iban", "label": "SWIFT / IBAN (International)", "fieldtype": "Data"},

            # 7 CATEGORY-SPECIFIC DETAILS
            {"fieldname": "section_7", "label": "Category-Specific Details", "fieldtype": "Section Break"},
            
            # 7A — HR / Staffing Partner
            {"fieldname": "sb_7a", "label": "HR / Staffing Partner Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'HR / Staffing Partner'"},
            {"fieldname": "hr_skills", "label": "Technologies / Skills", "fieldtype": "Table", "options": "Vendor HR Skill"},
            {"fieldname": "it_staffing", "label": "IT Staffing", "fieldtype": "Check"},
            {"fieldname": "non_it_staffing", "label": "Non-IT Staffing", "fieldtype": "Check"},
            {"fieldname": "both_staffing", "label": "Both", "fieldtype": "Check"},
            {"fieldname": "cb_7a", "fieldtype": "Column Break"},
            {"fieldname": "bulk_hiring_capacity", "label": "Bulk Hiring Capacity (per month)", "fieldtype": "Int"},
            {"fieldname": "standard_notice_period", "label": "Standard Notice Period Support", "fieldtype": "Data"},

            # 7B — Travel Vendor
            {"fieldname": "sb_7b", "label": "Travel Vendor Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'Travel Vendor'"},
            {"fieldname": "visa_assistance", "label": "Visa Assistance", "fieldtype": "Check"},
            {"fieldname": "air_rail_ticketing", "label": "Air / Rail Ticketing", "fieldtype": "Check"},
            {"fieldname": "cab_transport", "label": "Cab & Transport", "fieldtype": "Check"},
            {"fieldname": "support_24x7", "label": "24x7 Support", "fieldtype": "Check"},
            {"fieldname": "cb_7b", "fieldtype": "Column Break"},
            {"fieldname": "iata_accreditation_no", "label": "IATA Accreditation No.", "fieldtype": "Data"},
            {"fieldname": "fleet_size_categories", "label": "Fleet Size & Cab Categories", "fieldtype": "Data"},
            {"fieldname": "cities_serviced", "label": "Cities / Regions Serviced", "fieldtype": "Data"},

            # 7C — UPS / Power Backup Vendor
            {"fieldname": "sb_7c", "label": "UPS / Power Backup Vendor Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'UPS / Power Backup Vendor'"},
            {"fieldname": "brands_dealt", "label": "Brands Dealt / Authorised For", "fieldtype": "Data"},
            {"fieldname": "capacity_range", "label": "Capacity Range Supported (KVA)", "fieldtype": "Data"},
            {"fieldname": "cb_7c", "fieldtype": "Column Break"},
            {"fieldname": "response_sla", "label": "Response SLA (hours)", "fieldtype": "Data"},
            {"fieldname": "amc_support_available", "label": "AMC / Service Support Available", "fieldtype": "Check"},

            # 7D — Water & Utility Vendor
            {"fieldname": "sb_7d", "label": "Water & Utility Vendor Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'Water & Utility Vendor'"},
            {"fieldname": "water_can", "label": "Water Can", "fieldtype": "Check"},
            {"fieldname": "ro_unit", "label": "RO Unit", "fieldtype": "Check"},
            {"fieldname": "water_dispenser", "label": "Water Dispenser", "fieldtype": "Check"},
            {"fieldname": "cb_7d", "fieldtype": "Column Break"},
            {"fieldname": "delivery_frequency", "label": "Delivery Frequency", "fieldtype": "Data"},
            {"fieldname": "service_area", "label": "Service Area / Locations", "fieldtype": "Data"},
            {"fieldname": "contract_type", "label": "Contract Type", "fieldtype": "Select", "options": "\nRental\nOutright"},

            # 7E — Job Portal / Recruitment Platform
            {"fieldname": "sb_7e", "label": "Job Portal / Recruitment Platform Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'Job Portal / Recruitment Platform'"},
            {"fieldname": "platform_name", "label": "Platform Name", "fieldtype": "Data"},
            {"fieldname": "subscription_plans", "label": "Subscription Plans Offered", "fieldtype": "Data"},
            {"fieldname": "cb_7e", "fieldtype": "Column Break"},
            {"fieldname": "renewal_cycle", "label": "Renewal Cycle", "fieldtype": "Data"},
            {"fieldname": "account_manager_name", "label": "Account Manager Name & Contact", "fieldtype": "Data"},

            # 7F — Furniture Vendor
            {"fieldname": "sb_7f", "label": "Furniture Vendor Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'Furniture Vendor'"},
            {"fieldname": "seating", "label": "Seating", "fieldtype": "Check"},
            {"fieldname": "workstations", "label": "Workstations", "fieldtype": "Check"},
            {"fieldname": "storage", "label": "Storage", "fieldtype": "Check"},
            {"fieldname": "cabins", "label": "Cabins", "fieldtype": "Check"},
            {"fieldname": "cb_7f", "fieldtype": "Column Break"},
            {"fieldname": "customization_capability", "label": "Customization Capability", "fieldtype": "Select", "options": "\nYes\nNo"},
            {"fieldname": "typical_lead_time", "label": "Typical Lead Time", "fieldtype": "Data"},
            {"fieldname": "product_catalogue_attached", "label": "Product Catalogue Attached?", "fieldtype": "Select", "options": "\nYes\nNo"},

            # 7G — IT Hardware & Software Vendor
            {"fieldname": "sb_7g", "label": "IT Hardware & Software Vendor Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'IT Hardware & Software Vendor'"},
            {"fieldname": "bulk_laptop_supply", "label": "Bulk Laptop / Computer Supply", "fieldtype": "Check"},
            {"fieldname": "crm_implementation", "label": "CRM Implementation", "fieldtype": "Check"},
            {"fieldname": "erp_implementation", "label": "ERP Implementation", "fieldtype": "Check"},
            {"fieldname": "sitecore_cms", "label": "Sitecore / CMS", "fieldtype": "Check"},
            {"fieldname": "repair_amc_services", "label": "Repair & AMC Services", "fieldtype": "Check"},
            {"fieldname": "oem_reseller", "label": "OEM Reseller", "fieldtype": "Check"},
            {"fieldname": "cb_7g", "fieldtype": "Column Break"},
            {"fieldname": "oem_partnerships", "label": "OEM Partnerships", "fieldtype": "Data"},
            {"fieldname": "bulk_supply_capacity", "label": "Bulk Supply Capacity (units/month)", "fieldtype": "Int"},
            {"fieldname": "warranty_amc_support", "label": "Warranty / AMC Support", "fieldtype": "Select", "options": "\nYes\nNo"},

            # 7H — Individual Contractor / Consultant
            {"fieldname": "sb_7h", "label": "Individual Contractor / Consultant Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'Individual Contractor / Consultant'"},
            {"fieldname": "contractor_id", "label": "National ID / PAN / Passport No.", "fieldtype": "Data"},
            {"fieldname": "area_of_expertise", "label": "Area of Expertise", "fieldtype": "Data"},
            {"fieldname": "cb_7h", "fieldtype": "Column Break"},
            {"fieldname": "engagement_basis", "label": "Engagement Basis", "fieldtype": "Select", "options": "\nHourly\nDaily\nFixed"},
            {"fieldname": "rate", "label": "Rate", "fieldtype": "Currency"},
            {"fieldname": "availability", "label": "Availability", "fieldtype": "Data"},

            # 7I — General / Other
            {"fieldname": "sb_7i", "label": "General / Other Details", "fieldtype": "Section Break", "depends_on": "eval:doc.vendor_category == 'General / Other'"},
            {"fieldname": "general_nature_of_business", "label": "Nature of Business / Service", "fieldtype": "Small Text"},

            # 8 KYC DOCUMENT UPLOAD CHECKLIST
            {"fieldname": "section_8", "label": "KYC Document Upload Checklist", "fieldtype": "Section Break"},
            {"fieldname": "doc_gst", "label": "GST Certificate", "fieldtype": "Attach"},
            {"fieldname": "doc_pan", "label": "PAN Card", "fieldtype": "Attach"},
            {"fieldname": "doc_incorporation", "label": "Certificate of Incorporation / Partnership Deed", "fieldtype": "Attach"},
            {"fieldname": "doc_cheque", "label": "Cancelled Cheque", "fieldtype": "Attach"},
            {"fieldname": "doc_udyam", "label": "Udyam / MSME Certificate (optional)", "fieldtype": "Attach"},
            {"fieldname": "cb_8", "fieldtype": "Column Break"},
            {"fieldname": "doc_aadhaar", "label": "Aadhaar (masked)", "fieldtype": "Attach"},
            {"fieldname": "doc_tax_reg", "label": "Tax Registration Certificate (VAT/EIN/TIN)", "fieldtype": "Attach"},
            {"fieldname": "doc_bank_confirmation", "label": "Bank Confirmation Letter / IBAN Proof", "fieldtype": "Attach"},
            {"fieldname": "doc_w8ben", "label": "W-8BEN / W-8BEN-E", "fieldtype": "Attach"},
            {"fieldname": "doc_passport", "label": "Passport / National ID", "fieldtype": "Attach"},

            # 9 DECLARATION & SUBMISSION
            {"fieldname": "section_9", "label": "Declaration & Submission", "fieldtype": "Section Break"},
            {"fieldname": "declaration_text", "label": "Declaration", "fieldtype": "HTML", "options": "<p>I / We hereby declare that the information and documents furnished above are true and correct to the best of my/our knowledge. I / We agree to promptly inform Biztechnosys Infotech Pvt Ltd of any changes to the above details and consent to verification of the information and documents provided.</p>"},
            {"fieldname": "terms_accepted", "label": "I / We accept the Terms & Conditions and confirm the above declaration", "fieldtype": "Check", "reqd": 1},
            {"fieldname": "cb_9", "fieldtype": "Column Break"},
            {"fieldname": "authorised_signatory_name", "label": "Authorised Signatory Name", "fieldtype": "Data"},
            {"fieldname": "signatory_designation", "label": "Designation", "fieldtype": "Data"},
            {"fieldname": "signature_date", "label": "Date", "fieldtype": "Date"},

            # FOR OFFICE USE ONLY
            {"fieldname": "section_office", "label": "FOR OFFICE USE ONLY", "fieldtype": "Section Break"},
            {"fieldname": "stage", "label": "Stage", "fieldtype": "Data"},
            {"fieldname": "reviewed_by", "label": "Reviewed By", "fieldtype": "Link", "options": "User"},
            {"fieldname": "vendor_status", "label": "Status", "fieldtype": "Select", "options": "\nPending\nApproved\nSent Back\nRejected", "default": "Pending"},
            {"fieldname": "cb_office", "fieldtype": "Column Break"},
            {"fieldname": "l1_remarks", "label": "L1 — Verification (Procurement/Admin) Remarks", "fieldtype": "Small Text"},
            {"fieldname": "l2_remarks", "label": "L2 — Department Approval Remarks", "fieldtype": "Small Text"},
            {"fieldname": "l3_remarks", "label": "L3 — Compliance & Finance Check Remarks", "fieldtype": "Small Text"},
            {"fieldname": "l4_remarks", "label": "L4 — Final Approval (MD / CEO) Remarks", "fieldtype": "Small Text"}
        ]

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype_name,
            "module": "Custom Biz",
            "custom": 1,
            "istable": 0,
            "is_submittable": 0, # Usually forms can be submitted, let's keep it simple
            "autoname": "format:VEN-REG-{YYYY}-{#####}",
            "fields": fields,
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
            ]
        })
        doc.insert()
        print(f"DocType '{doctype_name}' created.")
    else:
        print(f"DocType '{doctype_name}' already exists.")

def run():
    create_child_table_poc()
    create_child_table_hr_skill()
    create_main_doctype()
    frappe.db.commit()

if __name__ == "__main__":
    run()
