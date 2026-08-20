import frappe
import json

def run():
    ws_meta = frappe.get_meta("Workspace")
    data = {
        "workspace_fields": [f.fieldname for f in ws_meta.fields]
    }
    print(json.dumps(data))
