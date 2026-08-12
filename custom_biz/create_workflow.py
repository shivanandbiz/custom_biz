import frappe

def create_workflow():
    states = ["Draft", "Pending Approval", "Approved", "Rejected"]
    for state in states:
        if not frappe.db.exists("Workflow State", state):
            frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state}).insert(ignore_permissions=True)

    actions = ["Submit for Approval", "Approve", "Reject", "Clarification Needed"]
    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(ignore_permissions=True)
            
    if not frappe.db.exists("Workflow", "Vendor Registration Approval"):
        doc = frappe.get_doc({
            "doctype": "Workflow",
            "module": "Custom Biz",
            "workflow_name": "Vendor Registration Approval",
            "document_type": "Vendor Registration",
            "is_active": 1,
            "send_email_alert": 0,
            "states": [
                {"state": "Draft", "doc_status": "0", "allow_edit": "All"},
                {"state": "Pending Approval", "doc_status": "0", "allow_edit": "System Manager"},
                {"state": "Approved", "doc_status": "1", "allow_edit": "System Manager"},
                {"state": "Rejected", "doc_status": "0", "allow_edit": "System Manager"}
            ],
            "transitions": [
                {"state": "Draft", "action": "Submit for Approval", "next_state": "Pending Approval", "allowed": "All"},
                {"state": "Pending Approval", "action": "Approve", "next_state": "Approved", "allowed": "System Manager"},
                {"state": "Pending Approval", "action": "Reject", "next_state": "Rejected", "allowed": "System Manager"},
                {"state": "Pending Approval", "action": "Clarification Needed", "next_state": "Draft", "allowed": "System Manager"}
            ]
        })
        doc.insert(ignore_permissions=True)
        
        # Add workflow_state field to Vendor Registration if it doesn't exist
        if not frappe.db.get_value("Custom Field", {"dt": "Vendor Registration", "fieldname": "workflow_state"}):
            from frappe.custom.doctype.custom_field.custom_field import create_custom_field
            create_custom_field("Vendor Registration", {
                "fieldname": "workflow_state",
                "label": "Workflow State",
                "fieldtype": "Link",
                "options": "Workflow State",
                "insert_after": "vendor_type",
                "hidden": 1
            })
            
        frappe.db.commit()
