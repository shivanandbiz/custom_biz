import frappe
import json

def run():
    task_meta = frappe.get_meta("Task")
    project_meta = frappe.get_meta("Project")
    
    data = {
        "task_fields": [f.fieldname for f in task_meta.fields],
        "project_fields": [f.fieldname for f in project_meta.fields]
    }
    print(json.dumps(data))
