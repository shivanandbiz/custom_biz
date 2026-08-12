import frappe

def run():
    report_name = "Employee Project Task Utilization"
    if not frappe.db.exists("Report", report_name):
        doc = frappe.get_doc({
            "doctype": "Report",
            "report_name": report_name,
            "ref_doctype": "Timesheet",
            "report_type": "Script Report",
            "is_standard": "Yes",
            "module": "Custom Biz"
        })
        doc.insert()
        frappe.db.commit()
        print(f"Report '{report_name}' created.")
    else:
        print(f"Report '{report_name}' already exists.")
